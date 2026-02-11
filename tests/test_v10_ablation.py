#!/usr/bin/env python3
"""
BALE V10 Ablation Study
Measures the contribution of each V10 component to overall risk detection.
Ablation conditions:
1. Classifier Only (baseline)
2. Classifier + Graph
3. Classifier + Graph + Power
4. Full V10 (Classifier + Graph + Power + Disputes)
"""
import json
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.v10.classifier_v10 import EmbeddingClassifier
from src.v10.contract_graph import build_contract_graph
from src.v10.power_analyzer import PowerAnalyzer
from src.v10.dispute_predictor import DisputePredictor
def load_test_contracts():
"""Load all evaluation contracts."""
contracts = []
dataset_dir = "evaluation/dataset"
for fname in os.listdir(dataset_dir):
if fname.endswith(".json"):
with open(os.path.join(dataset_dir, fname)) as f:
data = json.load(f)
if "text" in data:
contracts.append(data)
return contracts
def run_ablation():
classifier = EmbeddingClassifier(model_name="paraphrase-multilingual-MiniLM-L12-v2")
power_analyzer = PowerAnalyzer()
dispute_predictor = DisputePredictor()
contracts = load_test_contracts()
print(f"Loaded {len(contracts)} test contracts\n")
results = []
for contract in contracts:
text = contract["text"]
ctype = contract.get("type", "MSA")
name = contract.get("name", "Unknown")
expected_risk = contract.get("expected_risk", "unknown")
print(f"--- {name} (expected: {expected_risk}) ---")
# Chunk
import re
pattern = r'(?=(?:^|\n)\s*(?:(?:Section|Article|Clause)\s+)?\d{1,2}\.\s+[A-Z])'
sections = re.split(pattern, text, flags=re.IGNORECASE)
clauses = []
for i, s in enumerate(sections):
s = s.strip()
if len(s) > 30:
clauses.append({"id": f"s_{i}", "text": s[:3000]})
if not clauses:
paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
clauses = [{"id": f"p_{i}", "text": p[:2000]} for i, p in enumerate(paragraphs)]
# Phase 1: Classifier Only
t0 = time.time()
classified = []
for c in clauses:
result = classifier.classify(c["text"])
classified.append({
**c,
"clause_type": result.clause_type,
"confidence": result.confidence,
"risk_weight": classifier.get_risk_weight(result.clause_type),
})
avg_risk_weight = sum(c["risk_weight"] for c in classified) / max(len(classified), 1) * 100
classifier_risk = min(100, avg_risk_weight)
t1 = time.time()
# Phase 2: + Graph
graph, graph_analysis = build_contract_graph(classified, ctype)
graph_risk = graph_analysis.structural_risk
combined_cg = classifier_risk * 0.4 + graph_risk * 0.6
t2 = time.time()
# Phase 3: + Power
power_analysis = power_analyzer.analyze(classified, text)
combined_cgp = classifier_risk * 0.3 + graph_risk * 0.4 + power_analysis.power_score * 0.3
t3 = time.time()
# Phase 4: Full V10
dispute_prediction = dispute_predictor.predict(graph_analysis, power_analysis, classified)
full_risk = (
graph_analysis.structural_risk * 0.3
+ power_analysis.power_score * 0.2
+ dispute_prediction.overall_dispute_risk * 0.5
)
full_risk = min(100, full_risk)
t4 = time.time()
entry = {
"contract": name,
"expected_risk": expected_risk,
"clauses": len(classified),
"classifier_only": {
"risk_score": round(classifier_risk, 1),
"time_ms": int((t1 - t0) * 1000),
},
"classifier_graph": {
"risk_score": round(combined_cg, 1),
"conflicts": graph_analysis.conflict_count,
"gaps": graph_analysis.dependency_gap_count,
"missing": len(graph_analysis.missing_expected),
"completeness": round(graph_analysis.completeness_score, 2),
"time_ms": int((t2 - t0) * 1000),
},
"classifier_graph_power": {
"risk_score": round(combined_cgp, 1),
"power_score": round(power_analysis.power_score, 1),
"dominant": power_analysis.dominant_party,
"asymmetric_clauses": len(power_analysis.asymmetric_clauses),
"time_ms": int((t3 - t0) * 1000),
},
"full_v10": {
"risk_score": round(full_risk, 1),
"hotspots": len(dispute_prediction.hotspots),
"dispute_prediction": dispute_prediction.dispute_count_prediction,
"time_ms": int((t4 - t0) * 1000),
},
}
results.append(entry)
print(f" Classifier Only: {entry['classifier_only']['risk_score']:>6.1f} ({entry['classifier_only']['time_ms']}ms)")
print(f" + Graph: {entry['classifier_graph']['risk_score']:>6.1f} ({entry['classifier_graph']['time_ms']}ms) [{graph_analysis.conflict_count}C, {graph_analysis.dependency_gap_count}G, {len(graph_analysis.missing_expected)}M]")
print(f" + Power: {entry['classifier_graph_power']['risk_score']:>6.1f} ({entry['classifier_graph_power']['time_ms']}ms) [pwr={power_analysis.power_score:.0f}]")
print(f" Full V10: {entry['full_v10']['risk_score']:>6.1f} ({entry['full_v10']['time_ms']}ms) [{len(dispute_prediction.hotspots)} hotspots]")
print()
# Summary table
print("=" * 90)
print(f"{'Contract':<35} {'Expected':>8} {'C':>6} {'C+G':>6} {'C+G+P':>6} {'Full':>6}")
print("-" * 90)
for r in results:
print(f"{r['contract'][:34]:<35} {r['expected_risk']:>8} "
f"{r['classifier_only']['risk_score']:>6.1f} "
f"{r['classifier_graph']['risk_score']:>6.1f} "
f"{r['classifier_graph_power']['risk_score']:>6.1f} "
f"{r['full_v10']['risk_score']:>6.1f}")
print("=" * 90)
# Average latency
avg_full = sum(r["full_v10"]["time_ms"] for r in results) / max(len(results), 1)
print(f"\nAverage full pipeline latency: {avg_full:.0f}ms")
# Save results
with open("evaluation/v10_ablation_results.json", "w") as f:
json.dump({"ablation_study": results}, f, indent=2)
print("Results saved to evaluation/v10_ablation_results.json")
if __name__ == "__main__":
run_ablation()
