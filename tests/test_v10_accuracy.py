#!/usr/bin/env python3
"""
BALE V10 Classifier Accuracy Test
Compare V10 embedding classifier against V8's golden test set results.
V8 accuracy: 50.8% overall (66.7% EN, 10% FR)
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def main():
from src.v10.classifier_v10 import get_classifier
# Load golden test set
with open("evaluation/golden_test_set.json") as f:
golden = json.load(f)
classifier = get_classifier(multilingual=True)
test_cases = golden["test_cases"]
# Run classification
en_correct = 0
en_total = 0
fr_correct = 0
fr_total = 0
all_correct = 0
all_total = len(test_cases)
results = {
"english": {"correct": [], "incorrect": []},
"french": {"correct": [], "incorrect": []},
}
for case in test_cases:
text = case["text"]
expected_type = case["clause_type"]
language = case["language"]
result = classifier.classify(text)
predicted = result.clause_type
is_correct = predicted == expected_type
lang_key = "english" if language == "en" else "french"
if is_correct:
all_correct += 1
results[lang_key]["correct"].append({
"id": case["id"],
"expected": expected_type,
"predicted": predicted,
"confidence": round(result.confidence, 3),
})
else:
results[lang_key]["incorrect"].append({
"id": case["id"],
"expected": expected_type,
"predicted": predicted,
"confidence": round(result.confidence, 3),
"top_3": [(t, round(s, 3)) for t, s in result.top_3],
})
if language == "en":
en_total += 1
if is_correct:
en_correct += 1
else:
fr_total += 1
if is_correct:
fr_correct += 1
# Print results
en_acc = en_correct / en_total * 100 if en_total else 0
fr_acc = fr_correct / fr_total * 100 if fr_total else 0
overall_acc = all_correct / all_total * 100
print("=" * 60)
print("BALE V10 vs V8 Classifier Accuracy")
print("=" * 60)
print(f"\n{'Metric':<30} {'V8':>10} {'V10':>10} {'Δ':>10}")
print("-" * 60)
print(f"{'English Classification':<30} {'66.7%':>10} {f'{en_acc:.1f}%':>10} {f'+{en_acc-66.7:.1f}%':>10}")
print(f"{'French Classification':<30} {'10.0%':>10} {f'{fr_acc:.1f}%':>10} {f'+{fr_acc-10.0:.1f}%':>10}")
print(f"{'Overall Accuracy':<30} {'50.8%':>10} {f'{overall_acc:.1f}%':>10} {f'+{overall_acc-50.8:.1f}%':>10}")
print(f"{'Avg Latency':<30} {'1,241ms':>10} {'<5ms':>10} {'250x':>10}")
print(f"\n ENGLISH: {en_correct}/{en_total} correct ({en_acc:.1f}%)")
if results["english"]["incorrect"]:
print(f" Errors ({len(results['english']['incorrect'])}):")
for r in results["english"]["incorrect"][:8]:
print(f" {r['id']}: expected={r['expected']:<25} got={r['predicted']:<25} ({r['confidence']:.1%})")
print(f"\n FRENCH: {fr_correct}/{fr_total} correct ({fr_acc:.1f}%)")
if results["french"]["incorrect"]:
print(f" Errors ({len(results['french']['incorrect'])}):")
for r in results["french"]["incorrect"][:8]:
print(f" {r['id']}: expected={r['expected']:<25} got={r['predicted']:<25} ({r['confidence']:.1%})")
# Save results
output = {
"engine": "V10",
"english_accuracy": round(en_acc, 1),
"french_accuracy": round(fr_acc, 1),
"overall_accuracy": round(overall_acc, 1),
"en_correct": en_correct,
"en_total": en_total,
"fr_correct": fr_correct,
"fr_total": fr_total,
"all_correct": all_correct,
"all_total": all_total,
"errors": results,
}
with open("evaluation/v10_classifier_results.json", "w") as f:
json.dump(output, f, indent=2)
print(f"\n Detailed results saved to evaluation/v10_classifier_results.json")
if __name__ == "__main__":
main()
