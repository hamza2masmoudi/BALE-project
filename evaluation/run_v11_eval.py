#!/usr/bin/env python3
"""
BALE V11 Full-Scale Evaluation Runner
Runs the V11 pipeline on all evaluation contracts and optionally all 510 CUAD contracts.

Usage:
    python run_v11_eval.py                      # eval dataset only (15 contracts)
    python run_v11_eval.py --cuad-all           # eval dataset + ALL 510 CUAD contracts
    python run_v11_eval.py --cuad-sample 20     # eval dataset + 20 CUAD contracts
"""
import json, time, sys, os, csv, argparse, traceback
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.v10.pipeline import V10Pipeline, V10Report


def load_eval_contracts() -> list:
    """Load all 15 evaluation dataset contracts."""
    dataset_dir = Path(__file__).parent / "dataset"
    contracts = []
    for json_file in sorted(dataset_dir.glob("*.json")):
        if json_file.name == "manifest.json":
            continue
        with open(json_file) as f:
            data = json.load(f)
            if "text" in data:
                contracts.append({
                    "id": data.get("id", json_file.stem),
                    "name": data.get("name", json_file.stem),
                    "type": data.get("type", "MSA"),
                    "text": data["text"],
                    "expected_risk": data.get("expected_risk", "unknown"),
                    "source": "eval_dataset",
                })
    return contracts


def load_cuad_contracts(max_n: int = None) -> list:
    """Load CUAD contracts. If max_n is None, loads ALL."""
    cuad_dir = Path(__file__).parent.parent / "data" / "cuad_download" / "CUAD_v1" / "full_contract_txt"
    if not cuad_dir.exists():
        print(f"CUAD directory not found: {cuad_dir}")
        return []

    txt_files = sorted(cuad_dir.glob("*.txt"))
    if max_n is not None:
        txt_files = txt_files[:max_n]

    contracts = []
    for f in txt_files:
        try:
            text = f.read_text(errors="ignore")[:8000]  # First 8K chars
            if len(text.strip()) < 200:
                continue
            contracts.append({
                "id": f.stem[:60],
                "name": f.stem[:80],
                "type": _guess_type(f.name),
                "text": text,
                "expected_risk": "unknown",
                "source": "cuad",
            })
        except Exception:
            continue

    return contracts


def _guess_type(filename: str) -> str:
    """Infer contract type from CUAD filename."""
    fn = filename.lower()
    if "license" in fn:
        return "License"
    elif "service" in fn:
        return "MSA"
    elif "supply" in fn:
        return "Supply"
    elif "franchise" in fn:
        return "Franchise"
    elif "collaboration" in fn:
        return "Collaboration"
    elif "employment" in fn:
        return "Employment"
    elif "lease" in fn:
        return "Lease"
    elif "loan" in fn or "credit" in fn:
        return "Loan"
    elif "nda" in fn or "confidential" in fn:
        return "NDA"
    return "MSA"


def extract_metrics(report: V10Report) -> dict:
    """Extract all innovation metrics from a V10Report correctly."""
    metrics = {}

    # --- Classification metrics ---
    total_classified = 0
    human_review = 0
    confidences = []
    entropies = []
    margins = []
    for cls in report.clause_classifications:
        total_classified += 1
        if isinstance(cls, dict):
            if "calibrated_confidence" in cls:
                confidences.append(cls["calibrated_confidence"])
            if "entropy_ratio" in cls:
                entropies.append(cls["entropy_ratio"])
            if "margin" in cls:
                margins.append(cls["margin"])
            if cls.get("needs_human_review", False):
                human_review += 1

    metrics["total_classified"] = total_classified
    metrics["human_review_flagged"] = human_review
    metrics["avg_confidence"] = round(statistics.mean(confidences), 4) if confidences else 0
    metrics["avg_entropy"] = round(statistics.mean(entropies), 4) if entropies else 0
    metrics["avg_margin"] = round(statistics.mean(margins), 4) if margins else 0

    # --- Rewrite suggestions ---
    rewrites = report.suggested_rewrites or []
    metrics["num_rewrites"] = len(rewrites)
    risk_reductions = []
    for rw in rewrites:
        if isinstance(rw, dict) and "risk_reduction_pct" in rw:
            risk_reductions.append(rw["risk_reduction_pct"])
    metrics["avg_risk_reduction"] = round(statistics.mean(risk_reductions), 1) if risk_reductions else 0

    # --- Risk simulation ---
    sim = report.risk_simulation
    if sim and isinstance(sim, dict):
        metrics["sim_mean_risk"] = sim.get("mean_risk", 0)
        metrics["sim_ci_lower"] = sim.get("ci_95_lower", 0)
        metrics["sim_ci_upper"] = sim.get("ci_95_upper", 0)
        metrics["sim_ci_width"] = round(sim.get("ci_95_upper", 0) - sim.get("ci_95_lower", 0), 1)
        metrics["sim_volatility"] = sim.get("volatility_label", "unknown")
        metrics["sim_dominant_source"] = sim.get("dominant_uncertainty_source", "unknown")
    else:
        metrics["sim_mean_risk"] = 0
        metrics["sim_ci_width"] = 0
        metrics["sim_volatility"] = "none"

    # --- Corpus comparison ---
    corpus = report.corpus_comparison
    if corpus and isinstance(corpus, dict):
        anomalies = corpus.get("anomalies", [])
        metrics["num_anomalies"] = len(anomalies)
        metrics["anomaly_types"] = [a.get("metric", "?") if isinstance(a, dict) else str(a) for a in anomalies]
    else:
        metrics["num_anomalies"] = 0
        metrics["anomaly_types"] = []

    # --- Overall from report ---
    metrics["overall_risk"] = report.overall_risk_score
    metrics["risk_level"] = report.risk_level

    # --- Graph ---
    if isinstance(report.graph, dict):
        metrics["structural_risk"] = report.graph.get("structural_risk", 0)
        metrics["num_conflicts"] = len(report.graph.get("conflicts", []))
        metrics["completeness"] = report.graph.get("completeness_score", 0)
    else:
        metrics["structural_risk"] = 0

    # --- Power ---
    if isinstance(report.power, dict):
        metrics["power_score"] = report.power.get("power_score", 0)
    else:
        metrics["power_score"] = 0

    # --- Disputes ---
    if isinstance(report.disputes, dict):
        metrics["dispute_risk"] = report.disputes.get("overall_dispute_risk", 0)
        metrics["num_hotspots"] = len(report.disputes.get("hotspots", []))
    else:
        metrics["dispute_risk"] = 0

    return metrics


def run_evaluation(args):
    """Run the full-scale V11 evaluation."""
    print("=" * 70)
    print("BALE V11 Full-Scale Evaluation")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    # Load contracts
    eval_contracts = load_eval_contracts()
    if args.cuad_all:
        cuad_contracts = load_cuad_contracts(max_n=None)
    elif args.cuad_sample > 0:
        cuad_contracts = load_cuad_contracts(max_n=args.cuad_sample)
    else:
        cuad_contracts = []

    all_contracts = eval_contracts + cuad_contracts
    print(f"\nLoaded {len(eval_contracts)} eval dataset contracts")
    print(f"Loaded {len(cuad_contracts)} CUAD contracts")
    print(f"Total: {len(all_contracts)} contracts")
    print("-" * 70)

    # Initialize pipeline
    print("\nInitializing V11 pipeline...")
    t0 = time.time()
    pipeline = V10Pipeline(multilingual=True)
    init_time = time.time() - t0
    print(f"Pipeline initialized in {init_time:.1f}s")

    # Results accumulators
    results = []
    latencies = []
    errors = []
    by_type = defaultdict(list)

    # Aggregate innovation accumulators
    all_confidences = []
    all_entropies = []
    all_margins = []
    all_risk_reductions = []
    all_sim_risks = []
    all_ci_widths = []
    total_rewrites = 0
    total_anomalies = 0
    total_human_review = 0
    total_classified = 0

    # Process
    for i, contract in enumerate(all_contracts):
        print(f"\r[{i+1}/{len(all_contracts)}] {contract['name'][:55]:<55}", end="", flush=True)

        try:
            t_start = time.time()
            report = pipeline.analyze(
                contract_text=contract["text"],
                contract_type=contract["type"],
                suggest_rewrites=True,
                simulate_risk=True,
                corpus_compare=True,
                use_semantic_chunking=True,
            )
            latency_ms = int((time.time() - t_start) * 1000)
            latencies.append(latency_ms)

            m = extract_metrics(report)

            # Accumulate
            total_classified += m["total_classified"]
            total_human_review += m["human_review_flagged"]
            total_rewrites += m["num_rewrites"]
            total_anomalies += m["num_anomalies"]
            if m["avg_confidence"] > 0:
                all_confidences.append(m["avg_confidence"])
            if m["avg_entropy"] > 0:
                all_entropies.append(m["avg_entropy"])
            if m["avg_margin"] > 0:
                all_margins.append(m["avg_margin"])
            if m["avg_risk_reduction"] > 0:
                all_risk_reductions.append(m["avg_risk_reduction"])
            if m["sim_mean_risk"] > 0:
                all_sim_risks.append(m["sim_mean_risk"])
            if m["sim_ci_width"] > 0:
                all_ci_widths.append(m["sim_ci_width"])

            result = {
                "contract_id": contract["id"],
                "contract_name": contract["name"],
                "source": contract["source"],
                "contract_type": contract["type"],
                "expected_risk": contract["expected_risk"],
                "latency_ms": latency_ms,
                "status": "SUCCESS",
                **m,
            }
            results.append(result)
            by_type[contract["type"]].append(result)

            status_char = "✓"
            print(f" {status_char} {latency_ms}ms risk={m['overall_risk']:.0f} rw={m['num_rewrites']}")

        except Exception as e:
            latency_ms = int((time.time() - t_start) * 1000)
            result = {
                "contract_id": contract["id"],
                "contract_name": contract["name"],
                "source": contract["source"],
                "contract_type": contract["type"],
                "status": "ERROR",
                "error": str(e),
                "latency_ms": latency_ms,
            }
            results.append(result)
            errors.append(result)
            print(f" ✗ ERROR: {str(e)[:60]}")

    # === SUMMARY ===
    successful = [r for r in results if r["status"] == "SUCCESS"]
    n_success = len(successful)
    n_total = len(all_contracts)

    print("\n\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)
    print(f"\nContracts: {n_success}/{n_total} successful ({len(errors)} errors)")

    if latencies:
        print(f"\nLatency:")
        print(f"  Mean:   {statistics.mean(latencies):.0f}ms")
        print(f"  Median: {statistics.median(latencies):.0f}ms")
        print(f"  Std:    {statistics.stdev(latencies):.0f}ms" if len(latencies) > 1 else "")
        print(f"  P95:    {sorted(latencies)[int(len(latencies) * 0.95)]:.0f}ms")
        print(f"  Max:    {max(latencies):.0f}ms")

    print(f"\n--- Innovation Metrics ---")
    print(f"\n1. Classification & Calibration:")
    print(f"   Total classified:      {total_classified}")
    print(f"   Human review flagged:  {total_human_review} ({total_human_review/max(1,total_classified)*100:.1f}%)")
    print(f"   Avg confidence:        {statistics.mean(all_confidences):.4f}" if all_confidences else "   Avg confidence:        N/A")
    print(f"   Avg entropy ratio:     {statistics.mean(all_entropies):.4f}" if all_entropies else "   Avg entropy ratio:     N/A")
    print(f"   Avg margin:            {statistics.mean(all_margins):.4f}" if all_margins else "   Avg margin:            N/A")

    print(f"\n2. Rewrite Engine:")
    print(f"   Total suggestions:     {total_rewrites}")
    print(f"   Per contract:          {total_rewrites/max(1,n_success):.1f}")
    print(f"   Avg risk reduction:    {statistics.mean(all_risk_reductions):.1f}%" if all_risk_reductions else "   Avg risk reduction:    N/A")

    print(f"\n3. Monte Carlo Simulation:")
    print(f"   Simulations run:       {len(all_sim_risks)}/{n_success}")
    print(f"   Avg mean risk:         {statistics.mean(all_sim_risks):.1f}" if all_sim_risks else "   Avg mean risk:         N/A")
    print(f"   Avg CI width:          {statistics.mean(all_ci_widths):.1f}" if all_ci_widths else "   Avg CI width:          N/A")

    print(f"\n4. Corpus Intelligence:")
    print(f"   Contracts ingested:    {n_success}")
    print(f"   Total anomalies:       {total_anomalies}")

    # === PER-TYPE BREAKDOWN ===
    print(f"\n--- Per Contract Type ---")
    print(f"{'Type':<15} {'N':>3} {'AvgRisk':>8} {'AvgLat':>8} {'Rewrites':>8} {'Anomalies':>10}")
    print("-" * 55)
    for ctype in sorted(by_type.keys()):
        items = by_type[ctype]
        n = len(items)
        avg_risk = statistics.mean([r.get("overall_risk", 0) for r in items])
        avg_lat = statistics.mean([r.get("latency_ms", 0) for r in items])
        rw = sum(r.get("num_rewrites", 0) for r in items)
        an = sum(r.get("num_anomalies", 0) for r in items)
        print(f"{ctype:<15} {n:>3} {avg_risk:>8.1f} {avg_lat:>7.0f}ms {rw:>8} {an:>10}")

    # === SAVE JSON ===
    report_data = {
        "evaluation_info": {
            "timestamp": datetime.now().isoformat(),
            "version": "V11",
            "total_contracts": n_total,
            "successful": n_success,
            "failed": len(errors),
            "pipeline_init_time_s": round(init_time, 1),
            "eval_contracts": len(eval_contracts),
            "cuad_contracts": len(cuad_contracts),
        },
        "latency": {
            "mean_ms": round(statistics.mean(latencies)) if latencies else 0,
            "median_ms": round(statistics.median(latencies)) if latencies else 0,
            "std_ms": round(statistics.stdev(latencies)) if len(latencies) > 1 else 0,
            "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
            "max_ms": max(latencies) if latencies else 0,
        },
        "innovation_metrics": {
            "calibration": {
                "total_classified": total_classified,
                "human_review_flagged": total_human_review,
                "human_review_rate": round(total_human_review / max(1, total_classified), 4),
                "avg_confidence": round(statistics.mean(all_confidences), 4) if all_confidences else 0,
                "avg_entropy": round(statistics.mean(all_entropies), 4) if all_entropies else 0,
                "avg_margin": round(statistics.mean(all_margins), 4) if all_margins else 0,
            },
            "rewrite_engine": {
                "total_suggestions": total_rewrites,
                "per_contract": round(total_rewrites / max(1, n_success), 2),
                "avg_risk_reduction": round(statistics.mean(all_risk_reductions), 1) if all_risk_reductions else 0,
            },
            "risk_simulation": {
                "simulations_run": len(all_sim_risks),
                "avg_mean_risk": round(statistics.mean(all_sim_risks), 1) if all_sim_risks else 0,
                "avg_ci_width": round(statistics.mean(all_ci_widths), 1) if all_ci_widths else 0,
            },
            "corpus_intelligence": {
                "contracts_ingested": n_success,
                "total_anomalies": total_anomalies,
            },
        },
        "per_type_summary": {
            ctype: {
                "count": len(items),
                "avg_risk": round(statistics.mean([r.get("overall_risk", 0) for r in items]), 1),
                "avg_latency_ms": round(statistics.mean([r.get("latency_ms", 0) for r in items])),
                "total_rewrites": sum(r.get("num_rewrites", 0) for r in items),
                "total_anomalies": sum(r.get("num_anomalies", 0) for r in items),
            }
            for ctype, items in sorted(by_type.items())
        },
        "per_contract_results": results,
    }

    output_path = Path(__file__).parent / "v11_evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    # === SAVE CSV ===
    csv_path = Path(__file__).parent / "v11_evaluation_results.csv"
    if successful:
        fieldnames = [k for k in successful[0].keys() if k != "anomaly_types"]
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in results:
                writer.writerow({k: v for k, v in r.items() if k != "anomaly_types"})
        print(f"CSV saved to: {csv_path}")

    return report_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BALE V11 Evaluation")
    parser.add_argument("--cuad-all", action="store_true", help="Include ALL 510 CUAD contracts")
    parser.add_argument("--cuad-sample", type=int, default=0, help="Include N CUAD contracts")
    args = parser.parse_args()
    run_evaluation(args)
