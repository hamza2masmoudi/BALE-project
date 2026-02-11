import statistics
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.graph import compile_graph
from src.logger import setup_logger
logger = setup_logger("bale_benchmark")
def run_stability_benchmark(iterations: int = 10):
"""
Runs the BALE graph multiple times on 3 Unambiguous Clauses.
Goal: Standard Deviation < 5%.
"""
logger.info(f"Starting Stability Benchmark ({iterations} runs per clause)...")
clauses = [
{
"id": "STABLE_001_CLEAR_PAYMENT",
"text": "Payment is due within 30 days of invoice receipt. Interest accrues at 2% per annum thereafter."
},
{
"id": "STABLE_002_CLEAR_TERM",
"text": "This Agreement shall commence on Jan 1, 2024 and terminate on Dec 31, 2024."
},
{
"id": "STABLE_003_CLEAR_FORCE_MAJEURE",
"text": "Force Majeure means earthquake, fire, or flood. No other event qualifies."
}
]
app = compile_graph()
md_lines = []
passing = True
for clause in clauses:
cid = clause["id"]
text = clause["text"]
logger.info(f"Testing Stability: {cid}")
scores = []
for i in range(iterations):
try:
state = {"content": text}
result = app.invoke(state)
# Parse risk
report = result.get("final_report", {})
risk = report.get("risk", result.get("litigation_risk", 50))
scores.append(risk)
except Exception as e:
logger.error(f"Run {i} failed for {cid}: {e}")
scores.append(50) # Fallback
mean = statistics.mean(scores)
stdev = statistics.stdev(scores) if len(scores) > 1 else 0.0
icon = "" if stdev < 5.0 else ""
if stdev >= 5.0: passing = False
logger.info(f"{cid}: Mean={mean:.2f}, SD={stdev:.2f} {icon}")
md_lines.append(f"| {cid} | {mean:.2f}% | {stdev:.2f}% | {icon} |")
# Write Report
with open("evaluation/results_stability.md", "w") as f:
f.write("# Experiment C: Stability Benchmark Results\n\n")
f.write(f"**Date**: {os.popen('date').read().strip()}\n")
f.write(f"**Overall Result**: {'PASS' if passing else 'FAIL'}\n\n")
f.write("| Clause ID | Mean Risk | Standard Deviation | Result |\n")
f.write("| :--- | :--- | :--- | :--- |\n")
f.write("\n".join(md_lines))
if __name__ == "__main__":
run_stability_benchmark()
