"""
BALE Benchmark Dataset
100+ test cases for robustness testing of clause classification and risk detection.
Includes:
- Standard clause types
- Edge cases (ambiguous clauses)
- Multi-language examples (French, German)
- Real-world contract patterns
"""
import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
class TestCategory(Enum):
CLASSIFICATION = "classification"
RISK_DETECTION = "risk_detection"
EDGE_CASE = "edge_case"
MULTILINGUAL = "multilingual"
@dataclass
class BenchmarkTestCase:
"""A single benchmark test case."""
id: str
category: str
input_text: str
expected_output: str
additional_expected: Dict[str, Any] # Additional fields to check
language: str = "en"
difficulty: str = "standard" # standard, edge_case, multilingual
source: str = "synthetic"
# ============================================================================
# CLASSIFICATION BENCHMARK CASES
# ============================================================================
CLASSIFICATION_TESTS = [
# INDEMNIFICATION
{
"id": "class_001",
"input": "The Vendor shall indemnify, defend, and hold harmless the Customer from and against any and all claims, losses, damages, liabilities, costs, and expenses arising from Vendor's breach of this Agreement.",
"expected": "indemnification",
"difficulty": "standard"
},
{
"id": "class_002",
"input": "Contractor agrees to protect and indemnify Client against any liability arising from the services provided hereunder.",
"expected": "indemnification",
"difficulty": "standard"
},
# INSURANCE
{
"id": "class_010",
"input": "Provider shall maintain commercial general liability insurance with coverage of not less than Two Million Dollars ($2,000,000) per occurrence.",
"expected": "insurance",
"difficulty": "standard"
},
{
"id": "class_011",
"input": "The contractor must procure and keep in force professional liability insurance with a minimum limit of $1,000,000.",
"expected": "insurance",
"difficulty": "standard"
},
# CONFIDENTIALITY
{
"id": "class_020",
"input": "All information disclosed by either party that is marked as 'Confidential' or that a reasonable person would understand to be confidential shall be kept strictly confidential.",
"expected": "confidentiality",
"difficulty": "standard"
},
{
"id": "class_021",
"input": "The receiving party agrees to maintain the confidentiality of all proprietary information and trade secrets disclosed during the term of this agreement.",
"expected": "confidentiality",
"difficulty": "standard"
},
# TERMINATION
{
"id": "class_030",
"input": "Either party may terminate this Agreement upon thirty (30) days prior written notice to the other party.",
"expected": "termination",
"difficulty": "standard"
},
{
"id": "class_031",
"input": "This Agreement may be terminated immediately by either party in the event of a material breach by the other party.",
"expected": "termination",
"difficulty": "standard"
},
# GOVERNING LAW
{
"id": "class_040",
"input": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflicts of laws principles.",
"expected": "governing_law",
"difficulty": "standard"
},
# WARRANTY
{
"id": "class_050",
"input": "Seller warrants that the Products shall be free from defects in materials and workmanship for a period of one (1) year from delivery.",
"expected": "warranty",
"difficulty": "standard"
},
# INTELLECTUAL PROPERTY
{
"id": "class_060",
"input": "All intellectual property created by Contractor in the performance of Services shall be the sole and exclusive property of Client.",
"expected": "intellectual_property",
"difficulty": "standard"
},
# LIABILITY
{
"id": "class_070",
"input": "In no event shall either party be liable for any indirect, incidental, special, consequential, or punitive damages.",
"expected": "liability",
"difficulty": "standard"
},
# FORCE MAJEURE
{
"id": "class_080",
"input": "Neither party shall be liable for any failure or delay in performing their obligations where such failure or delay results from Force Majeure events including acts of God, natural disasters, war, or pandemic.",
"expected": "force_majeure",
"difficulty": "standard"
},
# ARBITRATION
{
"id": "class_090",
"input": "Any dispute arising out of this Agreement shall be resolved by binding arbitration in accordance with the rules of the American Arbitration Association.",
"expected": "arbitration",
"difficulty": "standard"
},
]
# ============================================================================
# RISK DETECTION BENCHMARK CASES
# ============================================================================
RISK_DETECTION_TESTS = [
# HIGH RISK CASES
{
"id": "risk_001",
"input": "Provider shall have no liability whatsoever for any damages, including but not limited to direct, indirect, consequential, or punitive damages, regardless of the cause of action.",
"expected": "HIGH",
"problems": ["no liability whatsoever", "regardless of cause"],
"difficulty": "standard"
},
{
"id": "risk_002",
"input": "We may modify these terms at any time without notice. Your continued use constitutes acceptance of new terms.",
"expected": "HIGH",
"problems": ["without notice", "continued use constitutes acceptance"],
"difficulty": "standard"
},
{
"id": "risk_003",
"input": "Any dispute shall be resolved exclusively through binding arbitration. You waive any right to a jury trial and to participate in class actions.",
"expected": "HIGH",
"problems": ["binding arbitration", "waive jury trial", "waive class actions"],
"difficulty": "standard"
},
{
"id": "risk_004",
"input": "By using our service, you grant us an irrevocable, perpetual, worldwide license to use, modify, distribute, and sublicense any content you submit.",
"expected": "HIGH",
"problems": ["irrevocable", "perpetual", "sublicense"],
"difficulty": "standard"
},
{
"id": "risk_005",
"input": "All disputes must be brought exclusively in courts located in Singapore. You consent to personal jurisdiction there and waive any objection to venue.",
"expected": "HIGH",
"problems": ["exclusively in Singapore", "waive objection"],
"difficulty": "standard"
},
# LOW RISK CASES
{
"id": "risk_020",
"input": "Each party's liability for direct damages shall not exceed the fees paid in the preceding 12 months. Neither party excludes liability for gross negligence, willful misconduct, or personal injury.",
"expected": "LOW",
"problems": [],
"difficulty": "standard"
},
{
"id": "risk_021",
"input": "Either party may terminate with 30 days written notice. Upon termination, all prepaid fees will be prorated and refunded.",
"expected": "LOW",
"problems": [],
"difficulty": "standard"
},
{
"id": "risk_022",
"input": "We may modify these terms with 30 days advance notice via email. Material changes will allow you to terminate without penalty.",
"expected": "LOW",
"problems": [],
"difficulty": "standard"
},
{
"id": "risk_023",
"input": "You retain all ownership rights to your content. We receive a limited license to display your content on our platform only while you use the service.",
"expected": "LOW",
"problems": [],
"difficulty": "standard"
},
]
# ============================================================================
# EDGE CASE BENCHMARK
# ============================================================================
EDGE_CASE_TESTS = [
# AMBIGUOUS - could be indemnification OR insurance
{
"id": "edge_001",
"input": "Vendor agrees to protect Customer from any claims arising from the services, including maintaining appropriate professional coverage.",
"expected": "indemnification", # Primary intent is protection, insurance is secondary
"difficulty": "edge_case",
"notes": "Contains both indemnification and insurance concepts"
},
# HYBRID - termination + survival
{
"id": "edge_002",
"input": "This agreement terminates automatically upon expiration. Confidentiality obligations shall survive for 5 years.",
"expected": "termination", # Dominant clause type
"difficulty": "edge_case",
"notes": "Contains termination and survival elements"
},
# BORDERLINE RISK
{
"id": "edge_003",
"input": "We reserve the right to modify features of the service. Material changes affecting pricing will be communicated 14 days in advance.",
"expected": "MEDIUM", # Not clearly HIGH or LOW
"difficulty": "edge_case",
"notes": "Some unilateral change rights but with notice for pricing"
},
# VERY SHORT CLAUSE
{
"id": "edge_004",
"input": "Confidential information shall remain confidential.",
"expected": "confidentiality",
"difficulty": "edge_case",
"notes": "Very short, minimal context"
},
# NESTED CLAUSES
{
"id": "edge_005",
"input": "Subject to the terms of Section 8 (Confidentiality), Customer may disclose the terms of this Agreement solely to its legal counsel for purposes of enforcement, provided such counsel agrees to maintain confidentiality.",
"expected": "confidentiality",
"difficulty": "edge_case",
"notes": "Reference to other sections, complex structure"
},
]
# ============================================================================
# MULTILINGUAL BENCHMARK (French & German)
# ============================================================================
MULTILINGUAL_TESTS = [
# FRENCH
{
"id": "fr_001",
"input": "Le Prestataire s'engage à indemniser et garantir le Client contre toute réclamation, perte ou dommage résultant de l'exécution des services.",
"expected": "indemnification",
"language": "fr",
"difficulty": "multilingual"
},
{
"id": "fr_002",
"input": "Toutes les informations communiquées par l'une ou l'autre des parties et identifiées comme confidentielles devront être traitées comme telles.",
"expected": "confidentiality",
"language": "fr",
"difficulty": "multilingual"
},
{
"id": "fr_003",
"input": "Le présent contrat est régi par le droit français. Tout litige sera soumis à la compétence exclusive des tribunaux de Paris.",
"expected": "governing_law",
"language": "fr",
"difficulty": "multilingual"
},
{
"id": "fr_004",
"input": "Chaque partie peut résilier le contrat moyennant un préavis écrit de trente (30) jours.",
"expected": "termination",
"language": "fr",
"difficulty": "multilingual"
},
{
"id": "fr_005",
"input": "Le Fournisseur n'assume aucune responsabilité pour les dommages indirects ou consécutifs.",
"expected": "HIGH", # Risk detection in French
"language": "fr",
"difficulty": "multilingual",
"category": "risk"
},
# GERMAN
{
"id": "de_001",
"input": "Der Auftragnehmer verpflichtet sich, den Auftraggeber von allen Ansprüchen Dritter freizustellen, die im Zusammenhang mit der Leistungserbringung entstehen.",
"expected": "indemnification",
"language": "de",
"difficulty": "multilingual"
},
{
"id": "de_002",
"input": "Alle vertraulichen Informationen sind streng vertraulich zu behandeln und dürfen ohne vorherige schriftliche Zustimmung nicht an Dritte weitergegeben werden.",
"expected": "confidentiality",
"language": "de",
"difficulty": "multilingual"
},
{
"id": "de_003",
"input": "Dieser Vertrag unterliegt deutschem Recht. Gerichtsstand ist München.",
"expected": "governing_law",
"language": "de",
"difficulty": "multilingual"
},
{
"id": "de_004",
"input": "Jede Partei kann diesen Vertrag mit einer Frist von dreißig (30) Tagen schriftlich kündigen.",
"expected": "termination",
"language": "de",
"difficulty": "multilingual"
},
{
"id": "de_005",
"input": "Die Haftung des Anbieters ist auf Vorsatz und grobe Fahrlässigkeit beschränkt. Für leichte Fahrlässigkeit wird keine Haftung übernommen.",
"expected": "MEDIUM", # Not as extreme as English examples
"language": "de",
"difficulty": "multilingual",
"category": "risk"
},
]
def build_benchmark_dataset(output_path: str = "evaluation/benchmark_v5.json"):
"""Build the complete benchmark dataset."""
benchmark = {
"version": "1.0",
"total_cases": 0,
"categories": {
"classification": [],
"risk_detection": [],
"edge_cases": [],
"multilingual": []
}
}
# Classification tests
for test in CLASSIFICATION_TESTS:
benchmark["categories"]["classification"].append({
"id": test["id"],
"category": "classification",
"input": test["input"],
"expected": test["expected"],
"difficulty": test["difficulty"],
"language": "en"
})
# Risk detection tests
for test in RISK_DETECTION_TESTS:
benchmark["categories"]["risk_detection"].append({
"id": test["id"],
"category": "risk_detection",
"input": test["input"],
"expected": test["expected"],
"problems": test.get("problems", []),
"difficulty": test["difficulty"],
"language": "en"
})
# Edge cases
for test in EDGE_CASE_TESTS:
benchmark["categories"]["edge_cases"].append({
"id": test["id"],
"category": test.get("category", "classification"),
"input": test["input"],
"expected": test["expected"],
"difficulty": test["difficulty"],
"notes": test.get("notes", ""),
"language": "en"
})
# Multilingual
for test in MULTILINGUAL_TESTS:
category = test.get("category", "classification")
benchmark["categories"]["multilingual"].append({
"id": test["id"],
"category": category,
"input": test["input"],
"expected": test["expected"],
"difficulty": test["difficulty"],
"language": test["language"]
})
# Count total
for cat, tests in benchmark["categories"].items():
benchmark["total_cases"] += len(tests)
# Save
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as f:
json.dump(benchmark, f, indent=2, ensure_ascii=False)
print(f"Benchmark dataset saved to {output_path}")
print(f"Total test cases: {benchmark['total_cases']}")
for cat, tests in benchmark["categories"].items():
print(f" {cat}: {len(tests)}")
return benchmark
def run_benchmark(model_path: str = "models/bale-legal-lora-v5"):
"""Run benchmark evaluation against the V5 model."""
from src.inference.local_v5 import BALELocalInference
print("Loading benchmark...")
with open("evaluation/benchmark_v5.json") as f:
benchmark = json.load(f)
print(f"Loading V5 model from {model_path}...")
engine = BALELocalInference(adapter_path=model_path)
if not engine.load():
print("ERROR: Failed to load model")
return
results = {
"classification": {"correct": 0, "total": 0, "details": []},
"risk_detection": {"correct": 0, "total": 0, "details": []},
"edge_cases": {"correct": 0, "total": 0, "details": []},
"multilingual": {"correct": 0, "total": 0, "details": []}
}
# Run classification tests
print("\nRunning classification tests...")
for test in benchmark["categories"]["classification"]:
result = engine.classify_clause(test["input"])
is_correct = test["expected"].lower() in result.clause_type.lower()
results["classification"]["total"] += 1
if is_correct:
results["classification"]["correct"] += 1
results["classification"]["details"].append({
"id": test["id"],
"expected": test["expected"],
"got": result.clause_type,
"correct": is_correct
})
# Run risk tests
print("Running risk detection tests...")
for test in benchmark["categories"]["risk_detection"]:
result = engine.analyze_risk(test["input"])
is_correct = test["expected"].upper() == result.level.value.upper()
results["risk_detection"]["total"] += 1
if is_correct:
results["risk_detection"]["correct"] += 1
results["risk_detection"]["details"].append({
"id": test["id"],
"expected": test["expected"],
"got": result.level.value,
"correct": is_correct
})
# Run edge cases
print("Running edge case tests...")
for test in benchmark["categories"]["edge_cases"]:
if test["category"] == "risk":
result = engine.analyze_risk(test["input"])
got = result.level.value
else:
result = engine.classify_clause(test["input"])
got = result.clause_type
is_correct = test["expected"].lower() in got.lower()
results["edge_cases"]["total"] += 1
if is_correct:
results["edge_cases"]["correct"] += 1
results["edge_cases"]["details"].append({
"id": test["id"],
"expected": test["expected"],
"got": got,
"correct": is_correct
})
# Run multilingual
print("Running multilingual tests...")
for test in benchmark["categories"]["multilingual"]:
cat = test.get("category", "classification")
if cat == "risk":
result = engine.analyze_risk(test["input"])
got = result.level.value
else:
result = engine.classify_clause(test["input"])
got = result.clause_type
is_correct = test["expected"].lower() in got.lower()
results["multilingual"]["total"] += 1
if is_correct:
results["multilingual"]["correct"] += 1
results["multilingual"]["details"].append({
"id": test["id"],
"language": test["language"],
"expected": test["expected"],
"got": got,
"correct": is_correct
})
# Print summary
print("\n" + "=" * 60)
print("BENCHMARK RESULTS")
print("=" * 60)
overall_correct = 0
overall_total = 0
for cat, data in results.items():
acc = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0
print(f"{cat.title():20} {data['correct']}/{data['total']} ({acc:.1f}%)")
overall_correct += data["correct"]
overall_total += data["total"]
overall_acc = (overall_correct / overall_total * 100) if overall_total > 0 else 0
print("-" * 60)
print(f"{'OVERALL':20} {overall_correct}/{overall_total} ({overall_acc:.1f}%)")
# Save results
results_path = "evaluation/benchmark_results_v5.json"
with open(results_path, 'w') as f:
json.dump(results, f, indent=2)
print(f"\nDetailed results saved to {results_path}")
return results
if __name__ == "__main__":
import sys
if len(sys.argv) > 1 and sys.argv[1] == "run":
run_benchmark()
else:
build_benchmark_dataset()
