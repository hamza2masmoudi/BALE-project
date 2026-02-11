"""
BALE V8 Advanced Risk Model
Probabilistic litigation risk prediction with multi-factor analysis.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import math
from src.logger import setup_logger
logger = setup_logger("bale_risk_model")
class PartyPosition(str, Enum):
"""Party position in contract."""
BUYER = "BUYER"
SELLER = "SELLER"
LICENSOR = "LICENSOR"
LICENSEE = "LICENSEE"
EMPLOYER = "EMPLOYER"
EMPLOYEE = "EMPLOYEE"
NEUTRAL = "NEUTRAL"
class LitigationOutcome(str, Enum):
"""Possible litigation outcomes."""
SETTLEMENT = "SETTLEMENT"
PLAINTIFF_WIN = "PLAINTIFF_WIN"
DEFENDANT_WIN = "DEFENDANT_WIN"
DISMISSAL = "DISMISSAL"
PARTIAL_WIN = "PARTIAL_WIN"
@dataclass
class RiskFactorWeight:
"""Weight and modifiers for a risk factor."""
base_weight: float # Base importance (0-1)
buyer_modifier: float = 0 # Adjustment for buyer (-0.5 to +0.5)
seller_modifier: float = 0 # Adjustment for seller
enforceability: float = 1.0 # How enforceable (0-1)
jurisdiction_uk: float = 1.0 # UK-specific adjustment
jurisdiction_fr: float = 1.0 # France-specific adjustment
# ==================== FACTOR DEFINITIONS ====================
RISK_FACTORS = {
# Clause-level factors
"ambiguity_score": RiskFactorWeight(
base_weight=0.15,
buyer_modifier=+0.05,
seller_modifier=-0.05,
enforceability=0.9
),
"exclusion_validity": RiskFactorWeight(
base_weight=0.12,
buyer_modifier=+0.08,
seller_modifier=-0.08,
jurisdiction_uk=1.2, # UCTA more strict
jurisdiction_fr=0.9
),
"hierarchy_violation": RiskFactorWeight(
base_weight=0.18,
enforceability=0.95,
jurisdiction_fr=1.3 # Civil law more formalistic
),
"precedent_strength": RiskFactorWeight(
base_weight=0.10,
jurisdiction_uk=1.2, # Common law precedent-driven
jurisdiction_fr=0.8
),
"drafting_quality": RiskFactorWeight(
base_weight=0.08,
enforceability=0.85
),
# Contract-level factors
"overall_balance": RiskFactorWeight(
base_weight=0.08,
buyer_modifier=+0.05,
seller_modifier=-0.05
),
"missing_clauses": RiskFactorWeight(
base_weight=0.07,
enforceability=0.8
),
"inconsistency": RiskFactorWeight(
base_weight=0.06,
enforceability=0.9
),
# External factors
"industry_litigation_rate": RiskFactorWeight(
base_weight=0.05
),
"jurisdiction_enforcement": RiskFactorWeight(
base_weight=0.06,
jurisdiction_uk=0.9,
jurisdiction_fr=1.1
),
"economic_conditions": RiskFactorWeight(
base_weight=0.03
),
"contract_value": RiskFactorWeight(
base_weight=0.02
),
}
# ==================== OUTCOME PREDICTIONS ====================
LITIGATION_OUTCOMES = {
LitigationOutcome.SETTLEMENT: {
"base_probability": 0.65,
"typical_recovery_range": (0.30, 0.70), # % of claimed damages
"time_to_resolution_months": (6, 18),
"legal_cost_range": (50000, 200000)
},
LitigationOutcome.PLAINTIFF_WIN: {
"base_probability": 0.18,
"typical_recovery_range": (0.50, 1.20),
"time_to_resolution_months": (18, 36),
"legal_cost_range": (150000, 500000)
},
LitigationOutcome.DEFENDANT_WIN: {
"base_probability": 0.12,
"typical_recovery_range": (0, 0),
"time_to_resolution_months": (18, 36),
"legal_cost_range": (150000, 400000)
},
LitigationOutcome.DISMISSAL: {
"base_probability": 0.03,
"typical_recovery_range": (0, 0),
"time_to_resolution_months": (3, 12),
"legal_cost_range": (30000, 100000)
},
LitigationOutcome.PARTIAL_WIN: {
"base_probability": 0.02,
"typical_recovery_range": (0.20, 0.50),
"time_to_resolution_months": (18, 30),
"legal_cost_range": (100000, 350000)
},
}
# ==================== RISK MODEL ====================
@dataclass
class RiskPrediction:
"""Complete risk prediction with confidence intervals."""
risk_score: float # Point estimate (0-100)
confidence_lower: float # Lower bound
confidence_upper: float # Upper bound
confidence_level: float # Confidence level (e.g., 0.95)
# Factor contributions
factor_contributions: Dict[str, float] = field(default_factory=dict)
# Jurisdiction-specific
uk_risk: float = 0
fr_risk: float = 0
# Outcome predictions
outcome_probabilities: Dict[str, float] = field(default_factory=dict)
# Expected values
expected_recovery: Tuple[float, float] = (0, 0)
expected_legal_costs: Tuple[float, float] = (0, 0)
expected_duration_months: Tuple[int, int] = (0, 0)
class LitigationRiskModel:
"""
Multi-factor probabilistic litigation risk model.
Based on empirical research on contract dispute resolution.
"""
def __init__(self):
self.factor_weights = RISK_FACTORS
self.outcomes = LITIGATION_OUTCOMES
def calculate_base_risk(self, factors: Dict[str, float]) -> float:
"""Calculate base risk score from factors."""
weighted_sum = 0
total_weight = 0
for factor_name, value in factors.items():
if factor_name in self.factor_weights:
weight = self.factor_weights[factor_name].base_weight
weighted_sum += value * weight
total_weight += weight
if total_weight > 0:
return (weighted_sum / total_weight) * 100
return 50 # Default medium risk
def adjust_for_party(self, base_risk: float, factors: Dict[str, float], party: PartyPosition) -> float:
"""Adjust risk based on party position."""
adjustment = 0
for factor_name, value in factors.items():
if factor_name in self.factor_weights:
fw = self.factor_weights[factor_name]
if party in [PartyPosition.BUYER, PartyPosition.LICENSEE, PartyPosition.EMPLOYEE]:
adjustment += value * fw.buyer_modifier * 100
elif party in [PartyPosition.SELLER, PartyPosition.LICENSOR, PartyPosition.EMPLOYER]:
adjustment += value * fw.seller_modifier * 100
return max(0, min(100, base_risk + adjustment))
def adjust_for_jurisdiction(self, base_risk: float, factors: Dict[str, float],
jurisdiction: str) -> float:
"""Adjust risk for specific jurisdiction."""
adjustment = 0
for factor_name, value in factors.items():
if factor_name in self.factor_weights:
fw = self.factor_weights[factor_name]
if jurisdiction == "UK":
adjustment += value * (fw.jurisdiction_uk - 1) * 10
elif jurisdiction == "FR":
adjustment += value * (fw.jurisdiction_fr - 1) * 10
return max(0, min(100, base_risk + adjustment))
def calculate_confidence_interval(self, risk_score: float, sample_size: int = 10,
confidence_level: float = 0.95) -> Tuple[float, float]:
"""Calculate confidence interval for risk score."""
# Use approximate standard error
std_error = math.sqrt(risk_score * (100 - risk_score) / max(1, sample_size))
# Z-score for confidence level
z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
z = z_scores.get(confidence_level, 1.96)
margin = z * std_error
lower = max(0, risk_score - margin)
upper = min(100, risk_score + margin)
return (lower, upper)
def predict_outcomes(self, risk_score: float) -> Dict[str, float]:
"""Predict litigation outcome probabilities given risk score."""
probabilities = {}
# Adjust base probabilities based on risk score
risk_factor = risk_score / 100
for outcome, data in self.outcomes.items():
base_prob = data["base_probability"]
if outcome == LitigationOutcome.PLAINTIFF_WIN:
# Higher risk = higher plaintiff win probability
adjusted = base_prob * (0.5 + risk_factor)
elif outcome == LitigationOutcome.DEFENDANT_WIN:
# Higher risk = lower defendant win probability
adjusted = base_prob * (1.5 - risk_factor)
elif outcome == LitigationOutcome.SETTLEMENT:
# Settlement slightly more likely at medium risk
if 30 <= risk_score <= 70:
adjusted = base_prob * 1.1
else:
adjusted = base_prob * 0.9
else:
adjusted = base_prob
probabilities[outcome.value] = min(1.0, max(0.01, adjusted))
# Normalize to sum to 1
total = sum(probabilities.values())
probabilities = {k: v/total for k, v in probabilities.items()}
return probabilities
def estimate_costs(self, risk_score: float, contract_value: float = 1000000) -> Dict:
"""Estimate expected litigation costs and recovery."""
outcome_probs = self.predict_outcomes(risk_score)
expected_recovery_low = 0
expected_recovery_high = 0
expected_costs_low = 0
expected_costs_high = 0
expected_duration_low = 0
expected_duration_high = 0
for outcome, prob in outcome_probs.items():
data = self.outcomes[LitigationOutcome(outcome)]
# Recovery
recovery_range = data["typical_recovery_range"]
expected_recovery_low += prob * recovery_range[0] * contract_value
expected_recovery_high += prob * recovery_range[1] * contract_value
# Costs
cost_range = data["legal_cost_range"]
expected_costs_low += prob * cost_range[0]
expected_costs_high += prob * cost_range[1]
# Duration
duration_range = data["time_to_resolution_months"]
expected_duration_low += prob * duration_range[0]
expected_duration_high += prob * duration_range[1]
return {
"expected_recovery": (expected_recovery_low, expected_recovery_high),
"expected_costs": (expected_costs_low, expected_costs_high),
"expected_duration_months": (int(expected_duration_low), int(expected_duration_high))
}
def predict(
self, factors: Dict[str, float],
party: PartyPosition = PartyPosition.NEUTRAL,
jurisdiction: str = "UK",
contract_value: float = 1000000,
confidence_level: float = 0.95
) -> RiskPrediction:
"""
Full risk prediction with all adjustments.
Args:
factors: Dict of factor names to values (0-1)
party: Party position for adjustment
jurisdiction: UK or FR
contract_value: Value of contract for cost estimation
confidence_level: Confidence level for intervals
Returns:
RiskPrediction with full analysis
"""
# Calculate base risk
base_risk = self.calculate_base_risk(factors)
# Adjust for party
party_adjusted = self.adjust_for_party(base_risk, factors, party)
# Adjust for jurisdiction
final_risk = self.adjust_for_jurisdiction(party_adjusted, factors, jurisdiction)
# Calculate both jurisdiction risks
uk_risk = self.adjust_for_jurisdiction(party_adjusted, factors, "UK")
fr_risk = self.adjust_for_jurisdiction(party_adjusted, factors, "FR")
# Confidence interval
lower, upper = self.calculate_confidence_interval(final_risk, confidence_level=confidence_level)
# Factor contributions
contributions = {}
for factor_name, value in factors.items():
if factor_name in self.factor_weights:
weight = self.factor_weights[factor_name].base_weight
contributions[factor_name] = value * weight * 100
# Outcome predictions
outcome_probs = self.predict_outcomes(final_risk)
# Cost estimation
costs = self.estimate_costs(final_risk, contract_value)
return RiskPrediction(
risk_score=final_risk,
confidence_lower=lower,
confidence_upper=upper,
confidence_level=confidence_level,
factor_contributions=contributions,
uk_risk=uk_risk,
fr_risk=fr_risk,
outcome_probabilities=outcome_probs,
expected_recovery=costs["expected_recovery"],
expected_legal_costs=costs["expected_costs"],
expected_duration_months=costs["expected_duration_months"]
)
# ==================== CLAUSE RISK CALCULATOR ====================
class ClauseRiskCalculator:
"""Calculate risk for specific clause types."""
# Clause type base risk scores
CLAUSE_BASE_RISKS = {
# High risk clauses
"exclusion_total": 85,
"non_compete_24mo": 80,
"mac_clause": 75,
"indemnification_broad": 75,
"exclusion_consequential": 70,
"earnout_provision": 70,
"limitation_liability": 65,
"ip_ownership_provider": 65,
"warranty_disclaimer": 65,
"residual_knowledge": 65,
# Medium risk clauses
"force_majeure_narrow": 55,
"gdpr_controller": 55,
"non_compete_12mo": 50,
"termination_convenience": 50,
"auto_renewal": 50,
"price_adjustment": 50,
"purchase_price_adjustment": 55,
"closing_conditions": 50,
"most_favored_customer": 50,
# Lower risk clauses
"indemnification_mutual": 40,
"indemnification_narrow": 35,
"warranty_express": 40,
"force_majeure_broad": 40,
"gdpr_processor": 40,
"data_transfer_scc": 40,
"confidentiality_mutual": 30,
"termination_cause": 30,
"cure_period": 25,
"arbitration_icc": 30,
"governing_law_uk": 25,
"governing_law_fr": 25,
"payment_terms_net30": 20,
"survival_clauses": 20,
}
def calculate(
self, clause_type: str,
party: PartyPosition = PartyPosition.NEUTRAL,
jurisdiction: str = "UK",
modifiers: Dict[str, float] = None
) -> Dict:
"""Calculate risk for a clause type."""
base_risk = self.CLAUSE_BASE_RISKS.get(clause_type, 50)
# Apply party modifier
if party in [PartyPosition.BUYER, PartyPosition.LICENSEE]:
# Buyers generally face more risk from unfavorable clauses
if base_risk > 50:
base_risk += 5
else:
base_risk -= 5
elif party in [PartyPosition.SELLER, PartyPosition.LICENSOR]:
if base_risk > 50:
base_risk -= 5
else:
base_risk += 5
# Apply jurisdiction modifier
if jurisdiction == "FR":
# French courts more protective of weaker party
if base_risk > 60:
base_risk -= 3
elif jurisdiction == "UK":
# UK courts more likely to enforce commercial terms
if base_risk > 60:
base_risk += 2
# Apply custom modifiers
if modifiers:
for mod_name, mod_value in modifiers.items():
base_risk += mod_value
# Constrain to valid range
final_risk = max(0, min(100, base_risk))
# Determine risk level
if final_risk >= 70:
level = "HIGH"
elif final_risk >= 40:
level = "MEDIUM"
else:
level = "LOW"
return {
"clause_type": clause_type,
"risk_score": final_risk,
"risk_level": level,
"party": party.value,
"jurisdiction": jurisdiction
}
# Singleton instances
_risk_model: Optional[LitigationRiskModel] = None
_clause_calculator: Optional[ClauseRiskCalculator] = None
def get_risk_model() -> LitigationRiskModel:
"""Get risk model singleton."""
global _risk_model
if _risk_model is None:
_risk_model = LitigationRiskModel()
return _risk_model
def get_clause_calculator() -> ClauseRiskCalculator:
"""Get clause calculator singleton."""
global _clause_calculator
if _clause_calculator is None:
_clause_calculator = ClauseRiskCalculator()
return _clause_calculator
# Export
__all__ = [
"PartyPosition",
"LitigationOutcome",
"RiskPrediction",
"LitigationRiskModel",
"ClauseRiskCalculator",
"get_risk_model",
"get_clause_calculator",
"RISK_FACTORS",
"LITIGATION_OUTCOMES"
]
