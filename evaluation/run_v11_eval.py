#!/usr/bin/env python3
"""
BALE V11 Innovations Evaluation Runner
Runs the full V11 pipeline (semantic chunking, calibrated classification,
clause rewriting, Monte Carlo risk simulation, corpus intelligence) against
the evaluation dataset and CUAD contracts.

Outputs a comprehensive JSON report with per-innovation metrics.
"""
import json
import time
import sys
import os
import glob
import traceback
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.v10.pipeline import V10Pipeline, V10Report


def load_eval_contracts() -> list:
    """Load all evaluation dataset contracts."""
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
                    "expected_findings": data.get("expected_findings", {}),
                    "source": "eval_dataset",
                })
    return contracts


def load_cuad_sample(n: int = 5) -> list:
    """Load a diverse sample of CUAD contracts."""
    cuad_dir = Path(__file__).parent.parent / "data" / "cuad_download" / "CUAD_v1" / "full_contract_txt"
    if not cuad_dir.exists():
        return []

    # Pick a diverse sample
    target_types = [
        "SERVICE AGREEMENT",
        "LICENSE AGREEMENT",
        "SUPPLY AGREEMENT",
        "COLLABORATION AGREEMENT",
        "FRANCHISE AGREEMENT",
    ]
    contracts = []
    txt_files = list(cuad_dir.glob("*.txt"))

    for target in target_types:
        for f in txt_files:
            if target.split()[0].lower() in f.name.lower() and len(contracts) < n:
                try:
                    text = f.read_text(errors="ignore")[:8000]  # First 8K chars
                    contracts.append({
                        "id": f.stem[:60],
                        "name": f.stem[:80],
                        "type": "MSA",
                        "text": text,
                        "expected_risk": "unknown",
                        "expected_findings": {},
                        "source": "cuad",
                    })
                    break
                except Exception:
                    continue

    return contracts


def run_evaluation():
    """Run the full V11 evaluation."""
    print("=" * 70)
    print("BALE V11 Innovations Evaluation")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    # Load contracts
    eval_contracts = load_eval_contracts()
    cuad_contracts = load_cuad_sample(5)
    all_contracts = eval_contracts + cuad_contracts

    print(f"\nLoaded {len(eval_contracts)} eval dataset contracts")
    print(f"Loaded {len(cuad_contracts)} CUAD sample contracts")
    print(f"Total: {len(all_contracts)} contracts to evaluate")
    print("-" * 70)

    # Initialize pipeline
    print("\nInitializing V11 pipeline...")
    t0 = time.time()
    pipeline = V10Pipeline(multilingual=True)
    init_time = time.time() - t0
    print(f"Pipeline initialized in {init_time:.1f}s")

    # Track metrics
    results = []
    latencies = []
    innovation_metrics = {
        "semantic_chunking": {"total_chunks": 0, "avg_chunks_per_contract": 0},
        "calibration": {
            "total_classified": 0,
            "human_review_flagged": 0,
            "avg_calibrated_confidence": 0,
            "avg_entropy_ratio": 0,
            "avg_margin": 0,
        },
        "rewrite_engine": {"total_suggestions": 0, "avg_risk_reduction": 0},
        "risk_simulation": {
            "simulations_run": 0,
            "avg_mean_risk": 0,
            "avg_ci_width": 0,
        },
        "corpus_intelligence": {"contracts_ingested": 0, "anomalies_flagged": 0},
    }
    confidence_values = []
    entropy_values = []
    margin_values = []
    risk_reductions = []
    mean_risks = []
    ci_widths = []

    # Run pipeline on each contract
    for i, contract in enumerate(all_contracts):
        contract_id = contract["id"]
        print(f"\n[{i+1}/{len(all_contracts)}] Analyzing: {contract['name'][:60]}...")

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

            # Extract innovation metrics from report
            report_dict = report.to_dict() if hasattr(report, 'to_dict') else {}

            # Semantic chunking metrics
            n_clauses = len(report.clauses) if hasattr(report, 'clauses') else 0
            innovation_metrics["semantic_chunking"]["total_chunks"] += n_clauses

            # Classification metrics
            if hasattr(report, 'classifications'):
                for cls in report.classifications:
                    innovation_metrics["calibration"]["total_classified"] += 1
                    if hasattr(cls, 'calibrated_confidence'):
                        confidence_values.append(cls.calibrated_confidence)
                    if hasattr(cls, 'entropy_ratio'):
                        entropy_values.append(cls.entropy_ratio)
                    if hasattr(cls, 'margin'):
                        margin_values.append(cls.margin)
                    if hasattr(cls, 'needs_human_review') and cls.needs_human_review:
                        innovation_metrics["calibration"]["human_review_flagged"] += 1

            # Rewrite suggestions
            if hasattr(report, 'suggested_rewrites') and report.suggested_rewrites:
                for rw in report.suggested_rewrites:
                    innovation_metrics["rewrite_engine"]["total_suggestions"] += 1
                    if isinstance(rw, dict) and "risk_reduction_pct" in rw:
                        risk_reductions.append(rw["risk_reduction_pct"])

            # Risk simulation
            if hasattr(report, 'risk_simulation') and report.risk_simulation:
                sim = report.risk_simulation
                innovation_metrics["risk_simulation"]["simulations_run"] += 1
                if isinstance(sim, dict):
                    if "mean_risk" in sim:
                        mean_risks.append(sim["mean_risk"])
                    if "ci_95_lower" in sim and "ci_95_upper" in sim:
                        ci_widths.append(sim["ci_95_upper"] - sim["ci_95_lower"])

            # Corpus intelligence
            if hasattr(report, 'corpus_comparison') and report.corpus_comparison:
                innovation_metrics["corpus_intelligence"]["contracts_ingested"] += 1
                corpus = report.corpus_comparison
                if isinstance(corpus, dict) and "anomalies" in corpus:
                    innovation_metrics["corpus_intelligence"]["anomalies_flagged"] += len(
                        corpus["anomalies"]
                    )

            result = {
                "contract_id": contract_id,
                "contract_name": contract["name"],
                "source": contract["source"],
                "contract_type": contract["type"],
                "expected_risk": contract["expected_risk"],
                "latency_ms": latency_ms,
                "num_clauses": n_clauses,
                "risk_score": report.risk_score if hasattr(report, 'risk_score') else None,
                "overall_risk": report_dict.get("overall_risk_score"),
                "graph_structural_risk": (
                    report.graph_analysis.structural_risk
                    if hasattr(report, 'graph_analysis') and report.graph_analysis
                    else None
                ),
                "power_score": (
                    report.power_analysis.power_score
                    if hasattr(report, 'power_analysis') and report.power_analysis
                    else None
                ),
                "dispute_risk": (
                    report.dispute_prediction.overall_dispute_risk
                    if hasattr(report, 'dispute_prediction') and report.dispute_prediction
                    else None
                ),
                "num_rewrite_suggestions": (
                    len(report.suggested_rewrites)
                    if hasattr(report, 'suggested_rewrites') and report.suggested_rewrites
                    else 0
                ),
                "has_risk_simulation": bool(
                    hasattr(report, 'risk_simulation') and report.risk_simulation
                ),
                "has_corpus_comparison": bool(
                    hasattr(report, 'corpus_comparison') and report.corpus_comparison
                ),
                "status": "SUCCESS",
            }
            results.append(result)

            print(f"   ✅ {latency_ms}ms | {n_clauses} clauses | "
                  f"risk={result.get('risk_score', '?')} | "
                  f"rewrites={result['num_rewrite_suggestions']} | "
                  f"sim={'✓' if result['has_risk_simulation'] else '✗'} | "
                  f"corpus={'✓' if result['has_corpus_comparison'] else '✗'}")

        except Exception as e:
            latency_ms = int((time.time() - t_start) * 1000)
            results.append({
                "contract_id": contract_id,
                "contract_name": contract["name"],
                "source": contract["source"],
                "status": "ERROR",
                "error": str(e),
                "latency_ms": latency_ms,
            })
            print(f"   ❌ ERROR: {str(e)[:100]}")
            traceback.print_exc()

    # Compute aggregate metrics
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)

    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] == "ERROR"]

    # Latency
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        max_latency = max(latencies)
    else:
        avg_latency = p95_latency = max_latency = 0

    # Finalize innovation metrics
    n_total = len(all_contracts)
    innovation_metrics["semantic_chunking"]["avg_chunks_per_contract"] = (
        round(innovation_metrics["semantic_chunking"]["total_chunks"] / max(1, len(successful)), 1)
    )

    if confidence_values:
        innovation_metrics["calibration"]["avg_calibrated_confidence"] = round(
            sum(confidence_values) / len(confidence_values), 4
        )
    if entropy_values:
        innovation_metrics["calibration"]["avg_entropy_ratio"] = round(
            sum(entropy_values) / len(entropy_values), 4
        )
    if margin_values:
        innovation_metrics["calibration"]["avg_margin"] = round(
            sum(margin_values) / len(margin_values), 4
        )
    if risk_reductions:
        innovation_metrics["rewrite_engine"]["avg_risk_reduction"] = round(
            sum(risk_reductions) / len(risk_reductions), 1
        )
    if mean_risks:
        innovation_metrics["risk_simulation"]["avg_mean_risk"] = round(
            sum(mean_risks) / len(mean_risks), 1
        )
    if ci_widths:
        innovation_metrics["risk_simulation"]["avg_ci_width"] = round(
            sum(ci_widths) / len(ci_widths), 1
        )

    # Print summary
    print(f"\nContracts analyzed: {len(successful)}/{n_total} successful")
    print(f"Errors: {len(failed)}")
    print(f"\nLatency:")
    print(f"  Average: {avg_latency:.0f}ms")
    print(f"  P95:     {p95_latency:.0f}ms")
    print(f"  Max:     {max_latency:.0f}ms")

    print(f"\n--- Innovation Metrics ---")
    print(f"\n1. Semantic Chunking:")
    print(f"   Total chunks: {innovation_metrics['semantic_chunking']['total_chunks']}")
    print(f"   Avg per contract: {innovation_metrics['semantic_chunking']['avg_chunks_per_contract']}")

    print(f"\n2. Confidence Calibration:")
    print(f"   Total classified: {innovation_metrics['calibration']['total_classified']}")
    print(f"   Human review flagged: {innovation_metrics['calibration']['human_review_flagged']}")
    print(f"   Avg calibrated confidence: {innovation_metrics['calibration']['avg_calibrated_confidence']}")
    print(f"   Avg entropy ratio: {innovation_metrics['calibration']['avg_entropy_ratio']}")
    print(f"   Avg margin: {innovation_metrics['calibration']['avg_margin']}")

    print(f"\n3. Rewrite Engine:")
    print(f"   Total suggestions: {innovation_metrics['rewrite_engine']['total_suggestions']}")
    print(f"   Avg risk reduction: {innovation_metrics['rewrite_engine']['avg_risk_reduction']}%")

    print(f"\n4. Monte Carlo Risk Simulation:")
    print(f"   Simulations run: {innovation_metrics['risk_simulation']['simulations_run']}")
    print(f"   Avg mean risk: {innovation_metrics['risk_simulation']['avg_mean_risk']}")
    print(f"   Avg CI width: {innovation_metrics['risk_simulation']['avg_ci_width']}")

    print(f"\n5. Corpus Intelligence:")
    print(f"   Contracts ingested: {innovation_metrics['corpus_intelligence']['contracts_ingested']}")
    print(f"   Anomalies flagged: {innovation_metrics['corpus_intelligence']['anomalies_flagged']}")

    # Save report
    report_data = {
        "evaluation_info": {
            "timestamp": datetime.now().isoformat(),
            "version": "V11",
            "total_contracts": n_total,
            "successful": len(successful),
            "failed": len(failed),
            "pipeline_init_time_s": round(init_time, 1),
        },
        "latency": {
            "avg_ms": round(avg_latency),
            "p95_ms": p95_latency,
            "max_ms": max_latency,
            "all_ms": latencies,
        },
        "innovation_metrics": innovation_metrics,
        "per_contract_results": results,
    }

    output_path = Path(__file__).parent / f"v11_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(report_data, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    # Also save to a stable filename
    stable_path = Path(__file__).parent / "v11_evaluation_results.json"
    with open(stable_path, "w") as f:
        json.dump(report_data, f, indent=2)
    print(f"Also saved to: {stable_path}")

    return report_data


if __name__ == "__main__":
    run_evaluation()
