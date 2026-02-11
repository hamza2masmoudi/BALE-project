#!/usr/bin/env python3
"""
BALE V8 Golden Test Set Evaluation Runner
Evaluates the trained model against the manually curated golden test set
to provide objective accuracy measurements.
Usage:
python run_golden_eval.py [--model-path PATH] [--output results.json]
"""
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
from mlx_lm import load, generate
MLX_AVAILABLE = True
except ImportError:
MLX_AVAILABLE = False
print("Warning: mlx_lm not available. Install with: pip install mlx-lm")
try:
from src.french_label_mapper import FrenchLabelMapper, detect_language
MAPPER_AVAILABLE = True
except ImportError:
MAPPER_AVAILABLE = False
detect_language = None
print("Warning: FrenchLabelMapper not available")
try:
from src.risk_analyzer import analyze_clause_risk, get_risk_prompt
RISK_ANALYZER_AVAILABLE = True
except ImportError:
RISK_ANALYZER_AVAILABLE = False
print("Warning: Risk analyzer not available")
class GoldenEvaluator:
"""Evaluates model against golden test set."""
def __init__(self, model_path: str = None, adapter_path: str = None):
self.model_path = model_path or "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
self.adapter_path = adapter_path or "models/bale-legal-lora-v8-ultimate"
self.model = None
self.tokenizer = None
self.french_mapper = FrenchLabelMapper() if MAPPER_AVAILABLE else None
# Valid clause types from taxonomy
self.valid_types = {
"indemnification", "limitation_of_liability", "termination",
"confidentiality", "intellectual_property", "governing_law",
"force_majeure", "warranty", "payment_terms", "non_compete",
"data_protection", "assignment", "dispute_resolution",
"insurance", "audit_rights"
}
# Risk levels
self.valid_risks = {"low", "medium", "high"}
def load_model(self):
"""Load the trained model."""
if not MLX_AVAILABLE:
raise RuntimeError("mlx_lm is required for evaluation")
print(f"Loading model: {self.model_path}")
print(f"Loading adapter: {self.adapter_path}")
adapter_full_path = Path(__file__).parent.parent / self.adapter_path
if adapter_full_path.exists():
self.model, self.tokenizer = load(
self.model_path,
adapter_path=str(adapter_full_path)
)
print(" Model loaded with adapter")
else:
self.model, self.tokenizer = load(self.model_path)
print(" Adapter not found, using base model")
def load_golden_set(self, path: str = None) -> dict:
"""Load the golden test set."""
golden_path = path or Path(__file__).parent / "golden_test_set.json"
with open(golden_path, 'r', encoding='utf-8') as f:
data = json.load(f)
print(f" Loaded {len(data['test_cases'])} golden test cases")
return data
def classify_clause(self, text: str) -> tuple[str, str, float]:
"""
Classify a clause and return (type, risk, latency_ms).
"""
prompt = f"""<s>[INST] You are a legal contract analyst. Analyze this clause and classify it.
Clause: {text}
Respond with:
1. Clause Type (one of: indemnification, limitation_of_liability, termination, confidentiality, intellectual_property, governing_law, force_majeure, warranty, payment_terms, non_compete, data_protection, assignment, dispute_resolution, insurance, audit_rights)
2. Risk Level (low, medium, high)
Format your response as:
Type: [type]
Risk: [level]
[/INST]"""
start_time = time.time()
response = generate(
self.model,
self.tokenizer,
prompt=prompt,
max_tokens=100,
verbose=False
)
latency_ms = (time.time() - start_time) * 1000
# Parse response
clause_type, risk_level = self._parse_response(response, text)
return clause_type, risk_level, latency_ms
def _parse_response(self, response: str, original_text: str = None) -> tuple[str, str]:
"""Parse model response to extract type and risk."""
response_lower = response.lower()
# Extract type
clause_type = "unknown"
for t in self.valid_types:
if t.replace("_", " ") in response_lower or t in response_lower:
clause_type = t
break
# Extract risk
risk_level = "unknown"
if "high" in response_lower:
risk_level = "high"
elif "medium" in response_lower:
risk_level = "medium"
elif "low" in response_lower:
risk_level = "low"
# Use French mapper for French text if available
if self.french_mapper and original_text and detect_language:
detected_lang = detect_language(original_text)
if detected_lang == 'fr':
result = self.french_mapper.parse_model_output(
response, is_french=True, input_text=original_text
)
if result.get("clause_type", "unknown") != "unknown":
# Map specialized types back to standard types
mapped_type = result["clause_type"]
for base_type in self.valid_types:
if base_type in mapped_type:
clause_type = base_type
break
# Use enhanced risk analyzer for HYBRID risk detection
if RISK_ANALYZER_AVAILABLE and original_text:
risk_result = analyze_clause_risk(original_text, response)
risk_level = risk_result["risk_level"]
else:
# Fallback to model output only
if "high" in response_lower:
risk_level = "high"
elif "medium" in response_lower:
risk_level = "medium"
elif "low" in response_lower:
risk_level = "low"
return clause_type, risk_level
def evaluate(self, golden_set: dict) -> dict:
"""Run full evaluation against golden set."""
results = {
"metadata": {
"timestamp": datetime.now().isoformat(),
"model_path": self.model_path,
"adapter_path": self.adapter_path,
"total_cases": len(golden_set["test_cases"])
},
"summary": {},
"by_language": {},
"by_type": {},
"by_risk": {},
"detailed_results": [],
"errors": []
}
# Counters
total_correct_type = 0
total_correct_risk = 0
total_correct_both = 0
total_latency = 0
by_lang = defaultdict(lambda: {"correct_type": 0, "correct_risk": 0, "total": 0})
by_type = defaultdict(lambda: {"correct": 0, "total": 0})
by_risk = defaultdict(lambda: {"correct": 0, "total": 0})
print("\n" + "="*60)
print("GOLDEN TEST SET EVALUATION")
print("="*60 + "\n")
for i, case in enumerate(golden_set["test_cases"]):
case_id = case["id"]
expected_type = case["clause_type"]
expected_risk = case["risk_level"]
text = case["text"]
language = case["language"]
print(f"[{i+1}/{len(golden_set['test_cases'])}] {case_id}...", end=" ")
try:
pred_type, pred_risk, latency = self.classify_clause(text)
type_match = pred_type == expected_type
risk_match = pred_risk == expected_risk
if type_match:
total_correct_type += 1
by_type[expected_type]["correct"] += 1
if risk_match:
total_correct_risk += 1
by_risk[expected_risk]["correct"] += 1
if type_match and risk_match:
total_correct_both += 1
by_lang[language]["total"] += 1
if type_match:
by_lang[language]["correct_type"] += 1
if risk_match:
by_lang[language]["correct_risk"] += 1
by_type[expected_type]["total"] += 1
by_risk[expected_risk]["total"] += 1
total_latency += latency
status = "" if type_match and risk_match else ("~" if type_match or risk_match else "")
print(f"{status} Type: {pred_type} ({'' if type_match else ''}) | Risk: {pred_risk} ({'' if risk_match else ''}) | {latency:.0f}ms")
results["detailed_results"].append({
"id": case_id,
"language": language,
"expected_type": expected_type,
"predicted_type": pred_type,
"type_correct": type_match,
"expected_risk": expected_risk,
"predicted_risk": pred_risk,
"risk_correct": risk_match,
"latency_ms": latency
})
except Exception as e:
print(f"ERROR: {e}")
results["errors"].append({
"id": case_id,
"error": str(e)
})
# Calculate summary metrics
n = len(golden_set["test_cases"])
results["summary"] = {
"type_accuracy": round(total_correct_type / n * 100, 2),
"risk_accuracy": round(total_correct_risk / n * 100, 2),
"combined_accuracy": round(total_correct_both / n * 100, 2),
"average_latency_ms": round(total_latency / n, 2),
"total_evaluated": n,
"errors": len(results["errors"])
}
# By language metrics
for lang, counts in by_lang.items():
results["by_language"][lang] = {
"type_accuracy": round(counts["correct_type"] / counts["total"] * 100, 2),
"risk_accuracy": round(counts["correct_risk"] / counts["total"] * 100, 2),
"total": counts["total"]
}
# By type metrics
for t, counts in by_type.items():
results["by_type"][t] = {
"accuracy": round(counts["correct"] / counts["total"] * 100, 2) if counts["total"] > 0 else 0,
"total": counts["total"]
}
# By risk metrics
for r, counts in by_risk.items():
results["by_risk"][r] = {
"accuracy": round(counts["correct"] / counts["total"] * 100, 2) if counts["total"] > 0 else 0,
"total": counts["total"]
}
# Print summary
print("\n" + "="*60)
print("EVALUATION SUMMARY")
print("="*60)
print(f"\n Overall Performance:")
print(f" Type Accuracy: {results['summary']['type_accuracy']}%")
print(f" Risk Accuracy: {results['summary']['risk_accuracy']}%")
print(f" Combined Accuracy: {results['summary']['combined_accuracy']}%")
print(f" Average Latency: {results['summary']['average_latency_ms']}ms")
print(f"\n By Language:")
for lang, metrics in results["by_language"].items():
print(f" {lang.upper()}: Type {metrics['type_accuracy']}% | Risk {metrics['risk_accuracy']}% ({metrics['total']} cases)")
print(f"\n By Clause Type:")
for t, metrics in sorted(results["by_type"].items(), key=lambda x: -x[1]["accuracy"]):
print(f" {t}: {metrics['accuracy']}% ({metrics['total']} cases)")
print(f"\n By Risk Level:")
for r, metrics in results["by_risk"].items():
print(f" {r}: {metrics['accuracy']}% ({metrics['total']} cases)")
if results["errors"]:
print(f"\n Errors: {len(results['errors'])}")
return results
def save_results(self, results: dict, output_path: str = None):
"""Save results to JSON file."""
output_path = output_path or Path(__file__).parent / f"golden_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_path, 'w', encoding='utf-8') as f:
json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n Results saved to: {output_path}")
def main():
parser = argparse.ArgumentParser(description="Evaluate BALE V8 against golden test set")
parser.add_argument("--model-path", default="mlx-community/Mistral-7B-Instruct-v0.3-4bit",
help="Path to base model")
parser.add_argument("--adapter-path", default="models/bale-legal-lora-v8-ultimate",
help="Path to LoRA adapter")
parser.add_argument("--golden-set", default=None,
help="Path to golden test set JSON")
parser.add_argument("--output", default=None,
help="Output path for results JSON")
parser.add_argument("--dry-run", action="store_true",
help="Load golden set without running model")
args = parser.parse_args()
evaluator = GoldenEvaluator(
model_path=args.model_path,
adapter_path=args.adapter_path
)
# Load golden set
golden_set = evaluator.load_golden_set(args.golden_set)
print(f"\n Golden Test Set Overview:")
print(f" Total cases: {len(golden_set['test_cases'])}")
# Count by language
lang_counts = defaultdict(int)
type_counts = defaultdict(int)
risk_counts = defaultdict(int)
for case in golden_set["test_cases"]:
lang_counts[case["language"]] += 1
type_counts[case["clause_type"]] += 1
risk_counts[case["risk_level"]] += 1
print(f" By language: {dict(lang_counts)}")
print(f" By risk: {dict(risk_counts)}")
print(f" Clause types covered: {len(type_counts)}")
if args.dry_run:
print("\n[Dry run - skipping model evaluation]")
return
# Run evaluation
evaluator.load_model()
results = evaluator.evaluate(golden_set)
evaluator.save_results(results, args.output)
if __name__ == "__main__":
main()
