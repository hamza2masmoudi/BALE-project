#!/usr/bin/env python3
"""
BALE V10 End-to-End Test
Run full pipeline on AI Services MSA from evaluation dataset.
"""
import json
import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def main():
# Load test contract
with open("evaluation/dataset/msa_ai_services.json") as f:
contract_data = json.load(f)
contract_text = contract_data["text"]
contract_type = contract_data["type"]
print(f"=== BALE V10 Test: {contract_data['name']} ===")
print(f"Type: {contract_type} | Expected Risk: {contract_data['expected_risk']}")
print(f"Parties: {', '.join(contract_data['parties'])}")
print("=" * 60)
# Run V10 pipeline
from src.v10.pipeline import V10Pipeline
pipeline = V10Pipeline(multilingual=True)
report = pipeline.analyze(contract_text, contract_type)
# Print results
print(f"\n ANALYSIS COMPLETE ({report.analysis_time_ms}ms)")
print(f"{'=' * 60}")
print(f"\n CLASSIFICATIONS ({report.total_clauses} clauses):")
for c in report.clause_classifications:
conf_bar = "█" * int(c["confidence"] * 20)
print(f" [{c['id']}] {c['clause_type']:25s} {c['confidence']:.1%} {conf_bar}")
print(f"\n GRAPH ANALYSIS:")
g = report.graph
print(f" Completeness: {g['completeness_score']:.0%}")
print(f" Structural Risk: {g['structural_risk']:.1f}/100")
print(f" Conflicts: {g['conflict_count']}")
for c in g["conflicts"]:
print(f" {c['clause_a']} vs {c['clause_b']}: {c['description']}")
print(f" Missing Dependencies: {g['dependency_gap_count']}")
for d in g["missing_dependencies"]:
print(f" {d['clause_has']} needs {d['clause_needs']}: {d['description']}")
print(f" Missing Expected: {len(g['missing_expected'])}")
for m in g["missing_expected"][:5]:
print(f" {m['clause_type']} (expected in {int(m['expected_prevalence']*100)}% of {contract_type}s)")
print(f"\n POWER ANALYSIS:")
p = report.power
print(f" Power Score: {p['power_score']:.1f}/100")
print(f" Dominant: {p['dominant_party']}")
print(f" Burdened: {p['burdened_party']}")
print(f" Asymmetric Clauses: {len(p['asymmetric_clauses'])}")
for a in p["asymmetric_clauses"][:3]:
print(f" {a['clause_type']} favors {a['favors']}")
print(f"\n DISPUTE HOTSPOTS:")
d = report.disputes
print(f" Overall Dispute Risk: {d['overall_dispute_risk']:.1f}/100")
print(f" Predicted Disputes: {d['dispute_count_prediction']}")
for h in d["hotspots"][:5]:
icon = "" if h["severity"] == "CRITICAL" else "" if h["severity"] == "HIGH" else ""
print(f" {icon} [{h['severity']}] {h['clause_type']}: {h['dispute_probability']:.0%}")
print(f" → {h['reason'][:80]}")
print(f"\n{'=' * 60}")
print(f" OVERALL: {report.risk_level} risk ({report.overall_risk_score:.1f}/100)")
print(f" {report.executive_summary}")
# Save full report
with open("evaluation/v10_test_report.json", "w") as f:
json.dump(report.to_dict(), f, indent=2)
print(f"\n Full report saved to evaluation/v10_test_report.json")
if __name__ == "__main__":
main()
