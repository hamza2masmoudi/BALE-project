"""
Demo: Full Neuro-Symbolic Loop (Standalone)
This script demonstrates the BALE V9 Architecture:
1. Debate Phase (Simulated LLM) -> High-level legal argumentation
2. Fact Phase (Simulated LLM) -> Extraction of boolean logic
3. Logic Phase (Real Logic Engine) -> Deductive reasoning
NOTE: This script uses a Mock class to avoid dependency errors (requests/langchain) in the demo environment, but uses the REAL src/logic/engine.py.
"""
import json
from src.logic.engine import InferenceEngine
from src.logic.rules_force_majeure import get_force_majeure_rules
# --- MOCK NEURAL COMPONENTS ---
class StandaloneMockDebateEngine:
"""
Simulates the 'Neural' part of the brain.
Implements the same interface as DebateEngine but returns canned responses
to prove the ARCHITECTURE works.
"""
def run_debate(self, clause_text, context, rounds=2):
print(f"Judge: We are here to debate: {clause_text}")
# Simulate Round 1
p_arg = "Plaintiff: This clause is ambiguous. The 50% cost increase is an external economic shock that effectively destroys the contract's equilibrium."
print(f"\n[Round 1 Plaintiff]: {p_arg}")
d_arg = "Defense: Economic hardship is NOT Force Majeure. The supplier accepted the risk of price fluctuation. The event is not 'irresistible'."
print(f"[Round 1 Defense]: {d_arg}")
# Simulate Judge Fact Extraction
print("\n[Judge] Extracting Facts from Debate...")
# Crucial Step: The 'Neural' engine maps the text arguments to 'Symbolic' booleans
facts = {
"is_ambiguous": True,
"is_external": True,
"is_unforeseeable": True,
"is_irresistible": False, # The Defense won this point (Economic != Irresistible)
"is_economic_change": True,
"is_strike": False,
"is_internal_dispute": False,
"contract_date_post_2020": False
}
return {
"transcript": [p_arg, d_arg],
"facts": facts
}
# --- MAIN PIPELINE ---
def run_neuro_symbolic_pipeline(scenario_name, clause_text, context):
print(f"\n{'='*50}")
print(f"SCENARIO: {scenario_name}")
print(f"{'='*50}")
# 1. RUN DEBATE (Neural - Mocked)
print("\n>>> PHASE 1: ADVERSARIAL DEBATE (Neural Discovery)")
debater = StandaloneMockDebateEngine()
result = debater.run_debate(clause_text, context)
facts = result["facts"]
print(f"\n>>> EXTRACTED FACTS (The Bridge):")
print(json.dumps(facts, indent=2))
# 2. RUN LOGIC (Symbolic - Real)
print("\n>>> PHASE 2: SYMBOLIC INFERENCE (Deductive Logic)")
engine = InferenceEngine()
for r in get_force_majeure_rules():
engine.add_rule(r)
for k, v in facts.items():
engine.set_fact(k, v)
verdict = engine.evaluate("is_valid_force_majeure")
print("\n>>> FINAL VERDICT:")
print(f"Is Valid Force Majeure? {verdict}")
print("\nReasoning Trace:")
for trace in engine.derivation_trace:
print(f" {trace}")
return verdict
if __name__ == "__main__":
result = run_neuro_symbolic_pipeline(
"Case A: Economic Hardship",
"The Supplier shall be excused from performance if raw material costs increase by more than 50%.",
"Supplier is trying to claim Force Majeure to cancel the contract due to inflation."
)
# Validation assertion for the demo
assert result is None, "Expected FM to be rejected (None/False)"
print("\n[SUCCESS] Pipeline correctly rejected Force Majeure based on economic hardship logic.")
