import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.graph import compile_graph
from src.logger import setup_logger
logger = setup_logger("bale_benchmark_soundness")
def run_soundness_benchmark():
"""
Runs BALE against the Gold Standard dataset.
Measures Directional Accuracy (Verdict Alignment).
"""
data_path = "tests/data/gold_standard.json"
if not os.path.exists(data_path):
logger.error(f"Gold Set not found at {data_path}")
return
with open(data_path, "r") as f:
cases = json.load(f)
logger.info(f"Starting Soundness Benchmark ({len(cases)} cases)...")
app = compile_graph()
stats = {"pass": 0, "fail": 0}
md_lines = []
for case in cases:
case_id = case["id"]
clause = case["clause"]
expected = case["expected_verdict"] # PLAINTIFF_WIN or DEFENSE_WIN
logger.info(f"Running Case: {case_id}...")
state = {"content": clause}
try:
result = app.invoke(state)
report = result.get("final_report", {})
# Extract Verdict / Risk
risk = report.get("risk", 50) # 0-100
# Map Risk to Verdict
# Risk > 50 => Plaintiff Favored
# Risk < 50 => Defense Favored
if risk > 50:
actual = "PLAINTIFF_WIN"
elif risk < 50:
actual = "DEFENSE_WIN"
else:
actual = "NEUTRAL"
# Compare
match = (actual == expected)
if match:
logger.info(f" PASS {case_id}: Expected {expected}, Got {actual} (Risk: {risk}%)")
stats["pass"] += 1
icon = ""
else:
logger.error(f" FAIL {case_id}: Expected {expected}, Got {actual} (Risk: {risk}%)")
stats["fail"] += 1
icon = ""
# Markdown Row
# Case | Expected | Actual | Risk | Result
md_lines.append(f"| {case_id} | {expected} | {actual} | {risk}% | {icon} |")
except Exception as e:
logger.error(f" ERROR {case_id}: {e}")
stats["fail"] += 1
md_lines.append(f"| {case_id} | {expected} | ERROR | N/A | |")
accuracy = (stats["pass"] / len(cases)) * 100
# Write Report
with open("evaluation/results_soundness.md", "w") as f:
f.write("# Experiment A: Soundness Benchmark Results\n\n")
f.write(f"**Date**: {os.popen('date').read().strip()}\n")
f.write(f"**Accuracy**: {accuracy:.2f}% ({stats['pass']}/{len(cases)})\n\n")
f.write("| Case ID | Expected | Actual | Risk | Result |\n")
f.write("| :--- | :--- | :--- | :--- | :--- |\n")
f.write("\n".join(md_lines))
logger.info("--- Benchmark Results ---")
accuracy = (stats["pass"] / len(cases)) * 100
logger.info("--- Benchmark Results ---")
logger.info(f"Total Cases: {len(cases)}")
logger.info(f"Passed: {stats['pass']}")
logger.info(f"Failed: {stats['fail']}")
logger.info(f"Directional Accuracy: {accuracy:.2f}%")
if accuracy >= 80:
logger.info(" PASS: System meets Research Grade Soundness (>80%)")
else:
logger.warning(" FAIL: System requires fine-tuning (<80%)")
if __name__ == "__main__":
run_soundness_benchmark()
