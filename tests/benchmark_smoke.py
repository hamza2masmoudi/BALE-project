import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.graph import compile_graph
from src.logger import setup_logger
logger = setup_logger("bale_benchmark_smoke")
def run_smoke_benchmark():
"""
Runs BALE against ONLY Case 001 from Gold Standard.
"""
data_path = "tests/data/gold_standard.json"
if not os.path.exists(data_path):
logger.error(f"Gold Set not found at {data_path}")
return
with open(data_path, "r") as f:
all_cases = json.load(f)
# SMOKE TEST FILTER: Case 001 only
cases = [c for c in all_cases if c["id"] == "CASE_001_AMBIGUOUS_EXCLUSION"]
if not cases:
logger.error("Filter error: CASE_001 not found in dataset.")
return
logger.info(f"Starting SMOKE Benchmark ({len(cases)} case)...")
app = compile_graph()
for case in cases:
case_id = case["id"]
clause = case["clause"]
expected = case["expected_verdict"] logger.info(f"Running Case: {case_id}...")
state = {"content": clause}
try:
result = app.invoke(state)
report = result.get("final_report", {})
risk = report.get("risk", 50) if risk > 50:
actual = "PLAINTIFF_WIN"
elif risk < 50:
actual = "DEFENSE_WIN"
else:
actual = "NEUTRAL"
match = (actual == expected)
if match:
logger.info(f" PASS {case_id}: Expected {expected}, Got {actual} (Risk: {risk}%)")
else:
logger.error(f" FAIL {case_id}: Expected {expected}, Got {actual} (Risk: {risk}%)")
except Exception as e:
logger.error(f" ERROR {case_id}: {e}")
if __name__ == "__main__":
run_smoke_benchmark()
