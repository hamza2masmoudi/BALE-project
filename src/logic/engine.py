"""
BALE Symbolic Logic Engine
A pure Python inference engine for first-order logic rules.
Replaces the hardcoded decision trees in adjudication.py.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
@dataclass
class Fact:
"""A base fact, e.g., Fact("is_unforeseeable", True)"""
name: str
value: Any
@dataclass
class Rule:
"""
A logical rule: IF (conditions) THEN (conclusion).
Example: IF (is_external AND is_unforeseeable) THEN (force_majeure)
"""
name: str
conditions: List[Dict[str, Any]] # List of {name: "is_external", value: True}
conclusion: Dict[str, Any] # {name: "valid_force_majeure", value: True}
strength: float = 1.0 # How strong is this rule (0-1)
class InferenceEngine:
def __init__(self):
self.rules: List[Rule] = []
self.facts: Dict[str, Any] = {}
self.derivation_trace: List[str] = []
def add_rule(self, rule: Rule):
self.rules.append(rule)
def set_fact(self, name: str, value: Any):
self.facts[name] = value
def evaluate(self, goal_name: str) -> Optional[Any]:
"""
Backward chaining to prove the goal.
Returns the value of the goal if proven, else None.
"""
# 1. Check if fact already exists
if goal_name in self.facts:
return self.facts[goal_name]
# 2. Find rules that conclude this goal
relevant_rules = [r for r in self.rules if r.conclusion['name'] == goal_name]
for rule in relevant_rules:
# Check all conditions for this rule
conditions_met = True
self.derivation_trace.append(f"Attempting to prove {goal_name} via Rule: {rule.name}")
for condition in rule.conditions:
cond_name = condition['name']
required_value = condition['value']
# Recursively evaluate condition
actual_value = self.evaluate(cond_name)
if actual_value != required_value:
conditions_met = False
self.derivation_trace.append(f" FAILED: {cond_name} is {actual_value}, needed {required_value}")
break
else:
self.derivation_trace.append(f" MATCH: {cond_name} is {actual_value}")
if conditions_met:
result_value = rule.conclusion['value']
self.facts[goal_name] = result_value
self.derivation_trace.append(f"SUCCESS: Proven {goal_name} = {result_value}")
return result_value
self.derivation_trace.append(f"FAIL: Could not prove {goal_name}")
return None
# Export
__all__ = ["Fact", "Rule", "InferenceEngine"]
