"""
Demo: Heuristic V8 vs Logic V9
Case Study: "The supplier cannot deliver due to a 50% increase in raw material costs."
"""
from src.logic.engine import InferenceEngine
from src.logic.rules_force_majeure import get_force_majeure_rules
def run_v8_heuristic(text: str):
"""Simulate V8's regex-based approach."""
print(f"\n[V8 Heuristic] Analyzing: '{text}'")
# V8 sees "cannot deliver" and assumes FM might apply, or misses it.
# If the clause says "costs", V8 might classify as "Price Adjustment" but relies on 'Risk: HIGH' template.
if "increase" in text and "cost" in text:
# V8 blindly tags this as a 'Risk' but might misses the FM invalidity nuance
return "RISK SCORING: Medium Risk (Ambiguous drafting)"
return "Unknown"
def run_v9_logic(facts: dict):
"""Run V9 Deductive Logic."""
print(f"\n[V9 Logic] Analyzing Facts: {facts}")
engine = InferenceEngine()
for r in get_force_majeure_rules():
engine.add_rule(r)
# Load facts extracted by LLM
for k, v in facts.items():
engine.set_fact(k, v)
# Query
is_fm = engine.evaluate("is_valid_force_majeure")
print("\n--- DERIVATION TRACE ---")
for step in engine.derivation_trace:
print(step)
return f"IS FORCE MAJEURE? {is_fm}"
if __name__ == "__main__":
# SCENARIO: Supplier claims Force Majeure because costs went up.
# Legal Reality: This is "Imprévision" (Hardship), NOT Force Majeure. FM requires Impossibility.
scenario_text = "Supplier claims force majeure due to 50% cost increase."
# V8 Result
print(run_v8_heuristic(scenario_text))
# V9 Result (LLM extracts these atomic facts first)
scenario_facts = {
"is_economic_change": True, # Cost increase = economic
"is_external": True, # Market price is external
"is_unforeseeable": True # Maybe unforeseeable
}
print(run_v9_logic(scenario_facts))
