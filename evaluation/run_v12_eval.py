#!/usr/bin/env python3
"""
BALE V12 Full-Scale Evaluation Runner
======================================
Runs the V12 Quad-Innovation engine on all evaluation contracts and [optionally]
all 510 CUAD contracts. Produces metrics suitable for the research paper:

  • Per-innovation statistics
  • Cross-innovation coherence
  • Latency benchmarks
  • Per-contract-type breakdown
  • Statistical significance indicators

Usage:
    python evaluation/run_v12_eval.py                     # eval dataset only
    python evaluation/run_v12_eval.py --cuad-all          # + ALL 510 CUAD contracts
    python evaluation/run_v12_eval.py --cuad-sample 50    # + 50 CUAD contracts
"""
import json, time, sys, os, csv, argparse, traceback
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.v10.pipeline import V10Pipeline, V10Report
from src.v12.v12_engine import V12Engine


# ==================== CONTRACT LOADERS ====================

def load_eval_contracts() -> list:
    """Load the 15 evaluation dataset contracts."""
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
            text = f.read_text(errors="ignore")[:8000]
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
    fn = filename.lower()
    for keyword, ctype in [
        ("license", "License"), ("service", "MSA"), ("supply", "Supply"),
        ("franchise", "Franchise"), ("collaboration", "Collaboration"),
        ("employment", "Employment"), ("lease", "Lease"),
        ("loan", "Loan"), ("credit", "Loan"), ("nda", "NDA"),
        ("confidential", "NDA"),
    ]:
        if keyword in fn:
            return ctype
    return "MSA"


# ==================== METRICS EXTRACTION ====================

def extract_v12_metrics(v12_report) -> dict:
    """Extract all V12 innovation metrics from a V12Report."""
    m = {}

    # Overall
    m["v11_risk"] = round(v12_report.v11_risk_score, 2)
    m["v12_fused_risk"] = round(v12_report.v12_fused_risk, 2)
    m["v12_confidence"] = round(v12_report.v12_confidence, 3)
    m["risk_delta"] = round(v12_report.v12_fused_risk - v12_report.v11_risk_score, 2)

    # Symbolic Reasoner
    sv = v12_report.symbolic_verdict
    if sv:
        m["sym_violations"] = sv.violations_triggered
        m["sym_risk"] = round(sv.symbolic_risk_score, 2)
        m["sym_fused"] = round(sv.fused_risk_score, 2)
        m["sym_alpha"] = round(sv.alpha, 3)
        m["sym_families"] = list(sv.doctrine_coverage.keys())
        m["sym_critical"] = sum(1 for v in sv.violations if v.severity == "critical")
        m["sym_high"] = sum(1 for v in sv.violations if v.severity == "high")
        m["sym_medium"] = sum(1 for v in sv.violations if v.severity == "medium")
    else:
        m["sym_violations"] = 0

    # RAG Case Law
    rag = v12_report.case_law_results
    if rag:
        m["rag_searched"] = rag.total_cases_searched
        m["rag_retrieved"] = rag.citations_retrieved
        m["rag_jurisdictions"] = rag.jurisdictions_covered
        m["rag_clause_types"] = rag.clause_types_analyzed
        if rag.citations:
            m["rag_avg_relevance"] = round(
                sum(c.relevance_score for c in rag.citations) / len(rag.citations), 3
            )
            m["rag_top_relevance"] = round(max(c.relevance_score for c in rag.citations), 3)
        else:
            m["rag_avg_relevance"] = 0
    else:
        m["rag_retrieved"] = 0

    # GNN
    gnn = v12_report.gnn_scores
    if gnn:
        m["gnn_graph_risk"] = round(gnn.graph_risk_score, 2)
        m["gnn_heuristic_risk"] = round(gnn.heuristic_risk, 2)
        m["gnn_anomaly"] = round(gnn.structural_anomaly_score, 3)
        m["gnn_nodes"] = len(gnn.node_results)
        m["gnn_edges"] = len(gnn.top_attention_edges)
        if gnn.node_results:
            deltas = [n.risk_delta for n in gnn.node_results]
            m["gnn_avg_delta"] = round(sum(deltas) / len(deltas), 3)
            m["gnn_max_delta"] = round(max(abs(d) for d in deltas), 3)
    else:
        m["gnn_graph_risk"] = 0

    # Debate
    debate = v12_report.debate_transcript
    if debate:
        m["debate_verdict"] = debate.final_verdict
        m["debate_sustained"] = sum(1 for r in debate.rulings if r.verdict == "sustained")
        m["debate_overruled"] = sum(1 for r in debate.rulings if r.verdict == "overruled")
        m["debate_risk_adj"] = round(debate.final_risk_adjustment, 3)
        m["debate_pro_args"] = len(debate.prosecution_arguments)
        m["debate_def_args"] = len(debate.defense_arguments)
        m["debate_duration_ms"] = debate.debate_duration_ms
    else:
        m["debate_verdict"] = "n/a"

    return m


# ==================== MAIN EVALUATION ====================

def run_evaluation(args):
    """Run the full-scale V12 evaluation."""
    print("=" * 80)
    print("BALE V12 Quad-Innovation — Full-Scale Evaluation")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 80)

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
    print("-" * 80)

    # Initialize engines
    print("\nInitializing V11 pipeline + V12 engine...")
    t0 = time.time()
    pipeline = V10Pipeline(multilingual=True)
    v12_engine = V12Engine()
    init_time = time.time() - t0
    print(f"Engines initialized in {init_time:.1f}s")

    # Accumulators
    results = []
    latencies_v11 = []
    latencies_v12 = []
    latencies_total = []
    errors = []
    by_type = defaultdict(list)

    # Per-innovation accumulators
    all_sym_violations = []
    all_sym_alphas = []
    all_sym_fused = []
    all_rag_retrieved = []
    all_rag_relevances = []
    all_gnn_risks = []
    all_gnn_anomalies = []
    all_gnn_deltas = []
    all_debate_sustained = []
    all_debate_overruled = []
    all_risk_deltas = []
    all_v12_confidences = []

    verdicts = defaultdict(int)

    # Process
    for i, contract in enumerate(all_contracts):
        print(f"\r[{i+1}/{len(all_contracts)}] {contract['name'][:50]:<50}", end="", flush=True)

        try:
            # V11 first
            t_v11 = time.time()
            v11_report = pipeline.analyze(
                contract_text=contract["text"],
                contract_type=contract["type"],
                suggest_rewrites=True,
                simulate_risk=True,
                corpus_compare=True,
                use_semantic_chunking=True,
            )
            v11_ms = int((time.time() - t_v11) * 1000)
            latencies_v11.append(v11_ms)

            # V12
            t_v12 = time.time()
            v12_report = v12_engine.analyze(v11_report)
            v12_ms = int((time.time() - t_v12) * 1000)
            latencies_v12.append(v12_ms)

            total_ms = v11_ms + v12_ms
            latencies_total.append(total_ms)

            # Extract metrics
            m = extract_v12_metrics(v12_report)
            m["v11_latency_ms"] = v11_ms
            m["v12_latency_ms"] = v12_ms
            m["total_latency_ms"] = total_ms

            # Accumulate
            all_sym_violations.append(m.get("sym_violations", 0))
            all_sym_alphas.append(m.get("sym_alpha", 0.5))
            all_sym_fused.append(m.get("sym_fused", 0))
            all_rag_retrieved.append(m.get("rag_retrieved", 0))
            if m.get("rag_avg_relevance", 0) > 0:
                all_rag_relevances.append(m["rag_avg_relevance"])
            all_gnn_risks.append(m.get("gnn_graph_risk", 0))
            all_gnn_anomalies.append(m.get("gnn_anomaly", 0))
            if "gnn_avg_delta" in m:
                all_gnn_deltas.append(m["gnn_avg_delta"])
            all_debate_sustained.append(m.get("debate_sustained", 0))
            all_debate_overruled.append(m.get("debate_overruled", 0))
            all_risk_deltas.append(m.get("risk_delta", 0))
            all_v12_confidences.append(m.get("v12_confidence", 0))
            if "debate_verdict" in m:
                verdicts[m["debate_verdict"]] += 1

            result = {
                "contract_id": contract["id"],
                "contract_name": contract["name"],
                "source": contract["source"],
                "contract_type": contract["type"],
                "expected_risk": contract["expected_risk"],
                "status": "SUCCESS",
                **m,
            }
            results.append(result)
            by_type[contract["type"]].append(result)

            print(f" ✓ {total_ms}ms v11={m['v11_risk']:.0f} v12={m['v12_fused_risk']:.0f} Δ={m['risk_delta']:+.1f} viol={m.get('sym_violations',0)} cites={m.get('rag_retrieved',0)}")

        except Exception as e:
            total_ms = int((time.time() - t_v11) * 1000)
            result = {
                "contract_id": contract["id"],
                "contract_name": contract["name"],
                "source": contract["source"],
                "contract_type": contract["type"],
                "status": "ERROR",
                "error": str(e),
                "total_latency_ms": total_ms,
            }
            results.append(result)
            errors.append(result)
            print(f" ✗ ERROR: {str(e)[:60]}")

    # ════════════════════ SUMMARY ════════════════════

    successful = [r for r in results if r["status"] == "SUCCESS"]
    n_success = len(successful)
    n_total = len(all_contracts)

    print("\n\n" + "=" * 80)
    print("V12 EVALUATION RESULTS")
    print("=" * 80)
    print(f"\nContracts: {n_success}/{n_total} successful ({len(errors)} errors)")

    # Latency
    if latencies_total:
        print(f"\n╔══ LATENCY ══════════════════════════════════════════════╗")
        print(f"║  V11 pipeline:  {statistics.mean(latencies_v11):>7.0f}ms mean  {statistics.median(latencies_v11):>7.0f}ms median")
        print(f"║  V12 engine:    {statistics.mean(latencies_v12):>7.0f}ms mean  {statistics.median(latencies_v12):>7.0f}ms median")
        print(f"║  Total:         {statistics.mean(latencies_total):>7.0f}ms mean  {statistics.median(latencies_total):>7.0f}ms median")
        if len(latencies_total) > 1:
            print(f"║  P95 total:     {sorted(latencies_total)[int(len(latencies_total) * 0.95)]:>7.0f}ms")
        print(f"╚═════════════════════════════════════════════════════════╝")

    # Innovation 1: Symbolic Reasoner
    print(f"\n╔══ 1. NEURO-SYMBOLIC REASONING ══════════════════════════╗")
    if all_sym_violations:
        print(f"║  Total violations triggered:  {sum(all_sym_violations)}")
        print(f"║  Mean violations/contract:    {statistics.mean(all_sym_violations):.2f}")
        print(f"║  Contracts with violations:   {sum(1 for v in all_sym_violations if v > 0)}/{n_success}")
        print(f"║  Mean α (blend factor):       {statistics.mean(all_sym_alphas):.3f}")
        print(f"║  Mean symbolic-fused risk:     {statistics.mean(all_sym_fused):.1f}")
        # Severity breakdown
        total_critical = sum(r.get("sym_critical", 0) for r in successful)
        total_high = sum(r.get("sym_high", 0) for r in successful)
        total_medium = sum(r.get("sym_medium", 0) for r in successful)
        print(f"║  By severity:  {total_critical} critical, {total_high} high, {total_medium} medium")
    print(f"╚═════════════════════════════════════════════════════════╝")

    # Innovation 2: RAG Case Law
    print(f"\n╔══ 2. RAG CASE LAW INTELLIGENCE ═════════════════════════╗")
    if all_rag_retrieved:
        print(f"║  Total citations retrieved:   {sum(all_rag_retrieved)}")
        print(f"║  Mean citations/contract:     {statistics.mean(all_rag_retrieved):.2f}")
        print(f"║  Mean relevance score:        {statistics.mean(all_rag_relevances):.3f}" if all_rag_relevances else "")
        # Jurisdiction breakdown
        all_juris = set()
        for r in successful:
            if "rag_jurisdictions" in r:
                all_juris.update(r["rag_jurisdictions"])
        print(f"║  Jurisdictions covered:       {sorted(all_juris)}")
    print(f"╚═════════════════════════════════════════════════════════╝")

    # Innovation 3: GNN
    print(f"\n╔══ 3. GRAPH ATTENTION NETWORK ═══════════════════════════╗")
    if all_gnn_risks:
        gnn_nonzero = [g for g in all_gnn_risks if g > 0]
        print(f"║  Mean graph risk:             {statistics.mean(gnn_nonzero):.1f}" if gnn_nonzero else "")
        print(f"║  Mean anomaly score:          {statistics.mean(all_gnn_anomalies):.3f}")
        print(f"║  Mean risk delta (GNN-heur):  {statistics.mean(all_gnn_deltas):.3f}" if all_gnn_deltas else "")
        high_anomaly = sum(1 for a in all_gnn_anomalies if a > 0.3)
        print(f"║  Structural anomalies (>0.3): {high_anomaly}/{n_success}")
    print(f"╚═════════════════════════════════════════════════════════╝")

    # Innovation 4: Debate
    print(f"\n╔══ 4. MULTI-AGENT LEGAL DEBATE ══════════════════════════╗")
    if all_debate_sustained:
        print(f"║  Total rulings:               {sum(all_debate_sustained) + sum(all_debate_overruled)}")
        print(f"║  Sustained:                   {sum(all_debate_sustained)}")
        print(f"║  Overruled:                   {sum(all_debate_overruled)}")
        sus_rate = sum(all_debate_sustained) / max(1, sum(all_debate_sustained) + sum(all_debate_overruled))
        print(f"║  Sustained rate:              {sus_rate:.1%}")
        print(f"║  Verdict breakdown:")
        for v, c in sorted(verdicts.items(), key=lambda x: -x[1]):
            print(f"║    {v}: {c} ({c/max(1,n_success)*100:.0f}%)")
    print(f"╚═════════════════════════════════════════════════════════╝")

    # Meta-Fusion Quality
    print(f"\n╔══ META-FUSION QUALITY ══════════════════════════════════╗")
    if all_risk_deltas:
        print(f"║  Mean V12-V11 risk delta:     {statistics.mean(all_risk_deltas):+.2f}")
        print(f"║  Std risk delta:              {statistics.stdev(all_risk_deltas):.2f}" if len(all_risk_deltas) > 1 else "")
        print(f"║  Mean V12 confidence:         {statistics.mean(all_v12_confidences):.3f}")
        increased = sum(1 for d in all_risk_deltas if d > 2)
        decreased = sum(1 for d in all_risk_deltas if d < -2)
        stable = n_success - increased - decreased
        print(f"║  Risk increased (Δ>2):        {increased}/{n_success}")
        print(f"║  Risk decreased (Δ<-2):       {decreased}/{n_success}")
        print(f"║  Risk stable (|Δ|≤2):         {stable}/{n_success}")
    print(f"╚═════════════════════════════════════════════════════════╝")

    # Per-type breakdown
    print(f"\n── Per Contract Type ──")
    header = f"{'Type':<15} {'N':>3} {'V11':>7} {'V12':>7} {'Δ':>6} {'Viol':>5} {'Cites':>5} {'Verdict':>12} {'Lat':>7}"
    print(header)
    print("-" * len(header))
    for ctype in sorted(by_type.keys()):
        items = by_type[ctype]
        n = len(items)
        avg_v11 = statistics.mean([r.get("v11_risk", 0) for r in items])
        avg_v12 = statistics.mean([r.get("v12_fused_risk", 0) for r in items])
        avg_delta = statistics.mean([r.get("risk_delta", 0) for r in items])
        viol = sum(r.get("sym_violations", 0) for r in items)
        cites = sum(r.get("rag_retrieved", 0) for r in items)
        most_verdict = max(set(r.get("debate_verdict", "n/a") for r in items), key=lambda v: sum(1 for r in items if r.get("debate_verdict") == v))
        avg_lat = statistics.mean([r.get("total_latency_ms", 0) for r in items])
        print(f"{ctype:<15} {n:>3} {avg_v11:>7.1f} {avg_v12:>7.1f} {avg_delta:>+5.1f} {viol:>5} {cites:>5} {most_verdict:>12} {avg_lat:>6.0f}ms")

    # Save JSON
    report_data = {
        "evaluation_info": {
            "timestamp": datetime.now().isoformat(),
            "engine_version": "V12",
            "total_contracts": n_total,
            "successful": n_success,
            "failed": len(errors),
            "pipeline_init_time_s": round(init_time, 1),
            "eval_contracts": len(eval_contracts),
            "cuad_contracts": len(cuad_contracts),
        },
        "latency": {
            "v11_mean_ms": round(statistics.mean(latencies_v11)) if latencies_v11 else 0,
            "v12_mean_ms": round(statistics.mean(latencies_v12)) if latencies_v12 else 0,
            "total_mean_ms": round(statistics.mean(latencies_total)) if latencies_total else 0,
            "total_median_ms": round(statistics.median(latencies_total)) if latencies_total else 0,
            "total_p95_ms": sorted(latencies_total)[int(len(latencies_total) * 0.95)] if latencies_total else 0,
        },
        "innovation_metrics": {
            "symbolic_reasoning": {
                "total_violations": sum(all_sym_violations),
                "mean_violations_per_contract": round(statistics.mean(all_sym_violations), 2) if all_sym_violations else 0,
                "contracts_with_violations": sum(1 for v in all_sym_violations if v > 0),
                "mean_alpha": round(statistics.mean(all_sym_alphas), 3) if all_sym_alphas else 0,
                "severity_critical": sum(r.get("sym_critical", 0) for r in successful),
                "severity_high": sum(r.get("sym_high", 0) for r in successful),
                "severity_medium": sum(r.get("sym_medium", 0) for r in successful),
            },
            "rag_case_law": {
                "total_citations": sum(all_rag_retrieved),
                "mean_citations_per_contract": round(statistics.mean(all_rag_retrieved), 2) if all_rag_retrieved else 0,
                "mean_relevance_score": round(statistics.mean(all_rag_relevances), 3) if all_rag_relevances else 0,
                "jurisdictions_covered": sorted(all_juris) if 'all_juris' in dir() else [],
            },
            "graph_attention_network": {
                "mean_graph_risk": round(statistics.mean([g for g in all_gnn_risks if g > 0]), 1) if [g for g in all_gnn_risks if g > 0] else 0,
                "mean_anomaly_score": round(statistics.mean(all_gnn_anomalies), 3) if all_gnn_anomalies else 0,
                "structural_anomalies_count": sum(1 for a in all_gnn_anomalies if a > 0.3),
                "mean_risk_delta": round(statistics.mean(all_gnn_deltas), 3) if all_gnn_deltas else 0,
            },
            "multi_agent_debate": {
                "total_rulings": sum(all_debate_sustained) + sum(all_debate_overruled),
                "sustained": sum(all_debate_sustained),
                "overruled": sum(all_debate_overruled),
                "sustained_rate": round(sum(all_debate_sustained) / max(1, sum(all_debate_sustained) + sum(all_debate_overruled)), 3),
                "verdict_distribution": dict(verdicts),
            },
        },
        "meta_fusion": {
            "mean_risk_delta": round(statistics.mean(all_risk_deltas), 2) if all_risk_deltas else 0,
            "std_risk_delta": round(statistics.stdev(all_risk_deltas), 2) if len(all_risk_deltas) > 1 else 0,
            "mean_confidence": round(statistics.mean(all_v12_confidences), 3) if all_v12_confidences else 0,
            "risk_increased": sum(1 for d in all_risk_deltas if d > 2),
            "risk_decreased": sum(1 for d in all_risk_deltas if d < -2),
            "risk_stable": n_success - sum(1 for d in all_risk_deltas if abs(d) > 2),
        },
        "per_type_summary": {
            ctype: {
                "count": len(items),
                "avg_v11_risk": round(statistics.mean([r.get("v11_risk", 0) for r in items]), 1),
                "avg_v12_risk": round(statistics.mean([r.get("v12_fused_risk", 0) for r in items]), 1),
                "avg_delta": round(statistics.mean([r.get("risk_delta", 0) for r in items]), 1),
                "total_violations": sum(r.get("sym_violations", 0) for r in items),
                "total_citations": sum(r.get("rag_retrieved", 0) for r in items),
                "avg_latency_ms": round(statistics.mean([r.get("total_latency_ms", 0) for r in items])),
            }
            for ctype, items in sorted(by_type.items())
        },
        "per_contract_results": results,
    }

    output_path = Path(__file__).parent / "v12_evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    # Save CSV
    csv_path = Path(__file__).parent / "v12_evaluation_results.csv"
    if successful:
        exclude_keys = {"anomaly_types", "sym_families", "rag_jurisdictions", "rag_clause_types"}
        fieldnames = [k for k in successful[0].keys() if k not in exclude_keys]
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in results:
                writer.writerow({k: v for k, v in r.items() if k not in exclude_keys})
        print(f"CSV saved to: {csv_path}")

    return report_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BALE V12 Evaluation")
    parser.add_argument("--cuad-all", action="store_true", help="Include ALL 510 CUAD contracts")
    parser.add_argument("--cuad-sample", type=int, default=0, help="Include N CUAD contracts")
    args = parser.parse_args()
    run_evaluation(args)
