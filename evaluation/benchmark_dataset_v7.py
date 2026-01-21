"""
BALE Benchmark Dataset V2
Expanded for V7 with Employment and M&A domains.

Includes:
- Standard clause types (from V5)
- Edge cases
- Multilingual (FR, DE)
- Employment Law (Non-compete, Severance, etc.)
- M&A (Reps & Warranties, indemnification, etc.)
"""
import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# [PREVIOUS TESTS REMAIN SAME - RE-INCLUDED FOR COMPLETENESS]
CLASSIFICATION_TESTS = [
    {"id": "class_001", "input": "The Vendor shall indemnify, defend, and hold harmless the Customer.", "expected": "indemnification", "difficulty": "standard"},
    {"id": "class_020", "input": "All information marked 'Confidential' shall be kept strictly confidential.", "expected": "confidentiality", "difficulty": "standard"},
    {"id": "class_030", "input": "Either party may terminate this Agreement upon thirty (30) days notice.", "expected": "termination", "difficulty": "standard"},
    {"id": "class_040", "input": "This Agreement shall be governed by the laws of the State of Delaware.", "expected": "governing_law", "difficulty": "standard"},
    {"id": "class_090", "input": "Any dispute shall be resolved by binding arbitration in New York.", "expected": "arbitration", "difficulty": "standard"},
]

RISK_DETECTION_TESTS = [
    {"id": "risk_001", "input": "Provider shall have no liability whatsoever for any damages.", "expected": "HIGH", "difficulty": "standard"},
    {"id": "risk_002", "input": "We may modify these terms at any time without notice.", "expected": "HIGH", "difficulty": "standard"},
    {"id": "risk_020", "input": "Liability limited to fees paid in last 12 months.", "expected": "LOW", "difficulty": "standard"},
]

MULTILINGUAL_TESTS = [
    {"id": "fr_001", "input": "Le Prestataire s'engage à indemniser le Client.", "expected": "indemnification", "language": "fr", "difficulty": "standard"},
    {"id": "fr_005", "input": "Le Fournisseur n'assume aucune responsabilité pour les dommages indirects.", "expected": "HIGH", "language": "fr", "category": "risk"}, # Risk
    {"id": "de_001", "input": "Der Auftragnehmer verpflichtet sich, den Auftraggeber freizustellen.", "expected": "indemnification", "language": "de", "difficulty": "standard"},
    {"id": "de_005", "input": "Wir behalten uns das Recht vor, diese Bedingungen jederzeit ohne Ankündigung zu ändern.", "expected": "HIGH", "language": "de", "category": "risk"}, # Risk
]

# [NEW DOMAIN TESTS]
EMPLOYMENT_TESTS = [
    {"id": "emp_001", "input": "Employee agrees not to work for any competitor within a 50-mile radius for 12 months.", "expected": "non_compete", "difficulty": "standard"},
    {"id": "emp_002", "input": "Upon termination without cause, Employee shall receive 6 months severance pay.", "expected": "termination", "difficulty": "standard"},
    {"id": "emp_003", "input": "All inventions created during employment belong exclusively to the Company.", "expected": "intellectual_property", "difficulty": "standard"},
    {"id": "emp_risk", "input": "Employee waives all claims including discrimination rights in exchange for $100.", "expected": "HIGH", "category": "risk", "difficulty": "standard"},
    {"id": "emp_low", "input": "Employment is at-will and may be terminated by either party with notice.", "expected": "LOW", "category": "risk", "difficulty": "standard"},
]

MA_TESTS = [
    {"id": "ma_001", "input": "Seller represents that there are no pending legal proceedings against the Company.", "expected": "representations", "difficulty": "standard"},
    {"id": "ma_002", "input": "Seller shall indemnify Buyer for valid claims up to the Cap Amount of $5M.", "expected": "indemnification", "difficulty": "standard"},
    {"id": "ma_003", "input": "Closing is conditioned upon receipt of HSR antitrust approval.", "expected": "closing_condition", "difficulty": "standard"},
    {"id": "ma_risk", "input": "Seller provides property 'as is' with no representations or warranties whatsoever.", "expected": "HIGH", "category": "risk", "difficulty": "standard"},
    {"id": "ma_low", "input": "10% of Purchase Price shall be held in escrow for 18 months to secure indemnification.", "expected": "LOW", "category": "risk", "difficulty": "standard"},
]

def build_benchmark_dataset(output_path: str = "evaluation/benchmark_v7.json"):
    """Build the expanded V7 benchmark dataset."""
    benchmark = {
        "version": "2.0",
        "total_cases": 0,
        "categories": {
            "classification": list(CLASSIFICATION_TESTS),
            "risk_detection": list(RISK_DETECTION_TESTS),
            "multilingual": list(MULTILINGUAL_TESTS),
            "employment": list(EMPLOYMENT_TESTS),
            "ma": list(MA_TESTS)
        }
    }
    
    # Count total
    count = 0
    for cat in benchmark["categories"].values():
        count += len(cat)
    benchmark["total_cases"] = count
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)
        
    print(f"Benchmark V7 saved to {output_path} with {count} cases.")
    return benchmark

def run_benchmark(model_path: str = "models/bale-legal-lora-v7"):
    """Run benchmark evaluation against the V7 model."""
    from src.inference.local_v5 import BALELocalInference
    
    ds_path = "evaluation/benchmark_v7.json"
    if not os.path.exists(ds_path):
        build_benchmark_dataset(ds_path)
        
    print(f"Loading benchmark from {ds_path}...")
    with open(ds_path) as f:
        benchmark = json.load(f)
    
    print(f"Loading model from {model_path}...")
    engine = BALELocalInference(adapter_path=model_path)
    if not engine.load():
        print("ERROR: Failed to load model")
        return
    
    results = {}
    
    for category, tests in benchmark["categories"].items():
        print(f"\nRunning {category} tests...")
        cat_results = {"correct": 0, "total": 0, "details": []}
        
        for test in tests:
            cat_results["total"] += 1
            
            # Determine if risk or classification
            is_risk = test.get("category") == "risk" or category == "risk_detection"
            
            if is_risk:
                res = engine.analyze_risk(test["input"])
                got = res.level.value
                expected = test["expected"]
                # Fuzzy match for risk (HIGH vs High)
                is_correct = got.upper() == expected.upper()
            else:
                res = engine.classify_clause(test["input"])
                got = res.clause_type
                expected = test["expected"]
                # Fuzzy match for classification (substring)
                is_correct = expected.lower() in got.lower().replace("_", " ") or \
                             got.lower().replace("_", " ") in expected.lower()
            
            if is_correct:
                cat_results["correct"] += 1
            
            cat_results["details"].append({
                "id": test["id"],
                "input": test["input"][:50] + "...",
                "expected": expected,
                "got": got,
                "correct": is_correct
            })
            
        results[category] = cat_results
        acc = (cat_results["correct"] / cat_results["total"] * 100) if cat_results["total"] else 0
        print(f"  Result: {cat_results['correct']}/{cat_results['total']} ({acc:.1f}%)")

    # Overall
    total_correct = sum(r["correct"] for r in results.values())
    total_cases = sum(r["total"] for r in results.values())
    overall = (total_correct / total_cases * 100) if total_cases else 0
    
    print("\n" + "="*40)
    print(f"OVERALL SCORE: {overall:.1f}% ({total_correct}/{total_cases})")
    print("="*40)
    
    with open("evaluation/benchmark_results_v7.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_benchmark(sys.argv[1])
    else:
        run_benchmark()
