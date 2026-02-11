from pydantic import BaseModel, Field
from typing import Tuple, List
class DecisionFactors(BaseModel):
is_ambiguous: bool = Field(description="Is the clause ambiguous/vague?")
is_exclusion_clear: bool = Field(description="Is the exclusion clause valid, clear, and unequivocal?")
authority_is_mandatory: bool = Field(description="Does the plaintiff cite Mandatory/Statutory law?")
plaintiff_plausible: bool = Field(description="Is the plaintiff's argument plausible by itself (>50%)?")
def calculate_litigation_risk(factors: DecisionFactors) -> Tuple[int, str]:
"""
Deterministically calculates Litigation Risk based on Boolean factors.
Returns (RiskPercent, VerdictString).
"""
risk = 50 # Baseline
verdict_parts = []
# 1. Ambiguity (Contra Proferentem) - Strongly favors Plaintiff (Risk UP)
if factors.is_ambiguous:
risk += 20
verdict_parts.append("AMBIGUOUS: Applying Contra Proferentem (Favors Plaintiff).")
else:
verdict_parts.append("CLEAR: No ambiguity found.")
# 2. Strict Construction of Exclusions - Favors Plaintiff if unclear (Risk UP)
if not factors.is_exclusion_clear:
risk += 15
verdict_parts.append("EXCLUSION FAILED: Strict Construction applied (Favors Plaintiff).")
# 3. Mandatory Authority - Overrides Contract (Risk UP UP)
if factors.authority_is_mandatory:
risk += 20
verdict_parts.append("AUTHORITY: Plaintiff cites Mandatory Law (Overrides Contract).")
# 4. Plausibility Check (Base merit)
if factors.plaintiff_plausible:
risk += 10
else:
risk -= 20
verdict_parts.append("WEAK CLAIM: Plaintiff argument implausible.")
# Cap Result
risk = max(0, min(100, risk))
verdict = " | ".join(verdict_parts)
return risk, verdict
