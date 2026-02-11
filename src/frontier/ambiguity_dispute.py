"""
Frontier VII: Strategic Ambiguity Coordination
Are multiple parties independently choosing the same ambiguities?
Frontier VIII: Predictive Dispute Cartography
Which specific clauses will become contested?
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
import re
import statistics
from src.frontier.core import corpus
from src.logger import setup_logger
logger = setup_logger("frontier_ambiguity")
# ==================== FRONTIER VII: STRATEGIC AMBIGUITY ====================
@dataclass
class AmbiguityPattern:
"""A pattern of strategic ambiguity across contracts."""
term: str
definition_variance: float # How differently it's defined
usage_count: int
jurisdictions: List[str]
industries: List[str]
first_seen: str
spread_velocity: float # How fast it's spreading
# Coordination signals
likely_coordinated: bool
coordination_evidence: List[str]
@dataclass
class AmbiguityAnalysis:
"""Analysis of ambiguity in an individual contract."""
contract_id: str
# Ambiguous terms found
ambiguous_terms: List[Dict[str, Any]]
total_ambiguity_score: float
# Market-level context
market_aligned_ambiguities: List[str] # Ambiguities matching market pattern
unique_ambiguities: List[str] # Ambiguities only in this contract
# Strategic interpretation
likely_intentional: List[str]
likely_accidental: List[str]
# Risk from ambiguity
interpretation_risk_score: int
def to_dict(self) -> Dict[str, Any]:
return asdict(self)
class StrategicAmbiguityTracker:
"""
Tracks ambiguity patterns across the contract corpus to detect
coordination, industry-wide deferral, and strategic vagueness.
"""
def __init__(self):
# Ambiguous term tracking
self.term_definitions: Dict[str, List[str]] = defaultdict(list)
self.term_appearances: Dict[str, List[Dict]] = defaultdict(list)
# Known vague terms
self.inherently_vague_terms = [
"reasonable", "material", "best efforts", "commercially reasonable",
"substantial", "prompt", "timely", "appropriate", "adequate",
"ordinary course", "good faith", "significant"
]
# Patterns suggesting intentional ambiguity
self.intentional_patterns = [
r"as determined by",
r"in its sole discretion",
r"as may be",
r"or otherwise",
r"including but not limited to",
r"and/or",
]
def record_term_usage(
self,
term: str,
definition: Optional[str],
contract_id: str,
jurisdiction: str,
industry: str,
date: str
):
"""Record usage of an ambiguous term."""
if definition:
self.term_definitions[term.lower()].append(definition)
self.term_appearances[term.lower()].append({
"contract_id": contract_id,
"jurisdiction": jurisdiction,
"industry": industry,
"date": date
})
def analyze_contract(
self,
contract_text: str,
contract_id: str,
jurisdiction: str,
industry: str
) -> AmbiguityAnalysis:
"""
Analyze ambiguity in a contract and compare to market patterns.
"""
text_lower = contract_text.lower()
# Find ambiguous terms
found_terms = []
for term in self.inherently_vague_terms:
count = text_lower.count(term)
if count > 0:
found_terms.append({
"term": term,
"count": count,
"type": "inherently_vague"
})
# Find intentional ambiguity patterns
for pattern in self.intentional_patterns:
matches = re.findall(pattern, text_lower)
if matches:
found_terms.append({
"term": pattern,
"count": len(matches),
"type": "intentional_pattern"
})
# Calculate total ambiguity score
total_score = sum(
t["count"] * (2 if t["type"] == "intentional_pattern" else 1)
for t in found_terms
)
# Compare to market patterns
market_aligned = []
unique = []
for term_info in found_terms:
term = term_info["term"]
if term in self.term_appearances:
# Check if other contracts use it similarly
appearances = self.term_appearances[term]
same_industry = sum(1 for a in appearances if a["industry"] == industry)
if same_industry > 2:
market_aligned.append(term)
else:
unique.append(term)
else:
unique.append(term)
# Classify intentional vs accidental
intentional = []
accidental = []
for term_info in found_terms:
term = term_info["term"]
if term_info["type"] == "intentional_pattern":
intentional.append(term)
elif term_info["count"] > 3: # Repeated use suggests intent
intentional.append(term)
else:
accidental.append(term)
# Calculate interpretation risk
interpretation_risk = min(100, total_score * 3)
return AmbiguityAnalysis(
contract_id=contract_id,
ambiguous_terms=found_terms,
total_ambiguity_score=total_score,
market_aligned_ambiguities=market_aligned,
unique_ambiguities=unique,
likely_intentional=intentional,
likely_accidental=accidental,
interpretation_risk_score=interpretation_risk
)
def detect_coordination(self) -> List[AmbiguityPattern]:
"""
Detect potential coordination in ambiguity across contracts.
"""
patterns = []
for term, appearances in self.term_appearances.items():
if len(appearances) < 3:
continue
# Calculate variance in definitions
definitions = self.term_definitions.get(term, [])
if definitions:
# Simple variance: unique definitions / total
unique_defs = len(set(d.lower() for d in definitions))
variance = unique_defs / len(definitions)
else:
variance = 1.0 # No definitions = maximum variance
# Calculate spread
jurisdictions = list(set(a["jurisdiction"] for a in appearances))
industries = list(set(a["industry"] for a in appearances))
# Calculate velocity
dates = sorted(a["date"] for a in appearances)
if len(dates) >= 2:
first = datetime.fromisoformat(dates[0])
last = datetime.fromisoformat(dates[-1])
days = max(1, (last - first).days)
velocity = len(appearances) / days * 30 # Per month
else:
velocity = 0
# Detect coordination signals
coordination_evidence = []
likely_coordinated = False
# Simultaneous emergence
if velocity > 5:
coordination_evidence.append("Rapid simultaneous adoption")
likely_coordinated = True
# Cross-competitor use
if len(industries) == 1 and len(appearances) > 5:
coordination_evidence.append("Industry-wide adoption")
likely_coordinated = True
# Definition convergence despite no standard
if variance < 0.3 and len(definitions) > 3:
coordination_evidence.append("Converging definitions without standard")
likely_coordinated = True
patterns.append(AmbiguityPattern(
term=term,
definition_variance=round(variance, 3),
usage_count=len(appearances),
jurisdictions=jurisdictions,
industries=industries,
first_seen=dates[0] if dates else "",
spread_velocity=round(velocity, 3),
likely_coordinated=likely_coordinated,
coordination_evidence=coordination_evidence
))
return sorted(patterns, key=lambda p: p.usage_count, reverse=True)
# ==================== FRONTIER VIII: DISPUTE CARTOGRAPHY ====================
@dataclass
class DisputePrediction:
"""Prediction of dispute for a specific clause."""
clause_text: str
clause_type: str
# Probability
dispute_probability: float
confidence: float
# Contributing factors
ambiguity_score: float
materiality_score: float
party_incentive_alignment: float # negative = misaligned
trigger_sensitivity: float # How sensitive to external triggers
# Predictions
likely_trigger_events: List[str]
expected_timeframe: str # "near" (<1y), "medium" (1-3y), "distant" (3+)
likely_outcome: str
def to_dict(self) -> Dict[str, Any]:
return asdict(self)
@dataclass
class DisputeCartography:
"""Full dispute map for a contract."""
contract_id: str
# Overall dispute risk
total_dispute_probability: float
high_risk_clause_count: int
# Clause predictions
clause_predictions: List[DisputePrediction]
# Interaction analysis
clause_interactions: List[Dict[str, Any]] # Clauses that amplify each other's risk
dispute_attractors: List[str] # Clause types likely to be focal points
# External factors
relevant_triggers: List[Dict[str, Any]]
economic_sensitivity: float
def to_dict(self) -> Dict[str, Any]:
d = asdict(self)
d["clause_predictions"] = [p.to_dict() for p in self.clause_predictions]
return d
class DisputePredictor:
"""
Predicts which specific clauses will become contested based on
ambiguity, materiality, party incentives, and trigger events.
"""
def __init__(self):
# Historical dispute rates by clause type
self.historical_dispute_rates = {
"indemnification": 0.15,
"limitation_liability": 0.12,
"force_majeure": 0.08,
"termination": 0.10,
"ip_assignment": 0.07,
"non_compete": 0.09,
"warranty": 0.11,
"payment": 0.13,
"confidentiality": 0.04,
}
# Trigger events and their clause impacts
self.trigger_impacts = {
"economic_downturn": {
"payment": 0.4,
"termination": 0.3,
"force_majeure": 0.2,
},
"regulatory_change": {
"data_protection": 0.5,
"compliance": 0.4,
},
"technology_disruption": {
"ip_assignment": 0.3,
"warranty": 0.2,
},
"pandemic": {
"force_majeure": 0.6,
"termination": 0.3,
},
"supply_chain": {
"delivery": 0.5,
"force_majeure": 0.3,
}
}
# Clause interaction amplifiers
self.interaction_amplifiers = [
(["indemnification", "limitation_liability"], 1.3, "Indemnification vs cap tension"),
(["termination", "non_compete"], 1.2, "Exit conflict"),
(["warranty", "limitation_liability"], 1.25, "Warranty vs liability cap"),
]
def predict_disputes(
self,
contract_text: str,
contract_id: str,
clause_analyses: List[Dict[str, Any]] = None,
party_context: Dict[str, Any] = None
) -> DisputeCartography:
"""
Generate dispute predictions for all clauses.
"""
# Parse clauses if not provided
if clause_analyses is None:
clause_analyses = self._extract_clauses(contract_text)
predictions = []
clause_types = []
for clause in clause_analyses:
prediction = self._predict_clause_dispute(clause, party_context)
predictions.append(prediction)
clause_types.append(clause.get("type", "unknown"))
# Find interactions
interactions = self._find_interactions(clause_types, predictions)
# Apply interaction amplifiers
for pred in predictions:
for types, amplifier, _ in self.interaction_amplifiers:
if pred.clause_type in types:
if all(t in clause_types for t in types):
pred.dispute_probability = min(1.0, pred.dispute_probability * amplifier)
# Calculate total probability
total_prob = 1 - statistics.mean([1 - p.dispute_probability for p in predictions]) if predictions else 0
high_risk_count = sum(1 for p in predictions if p.dispute_probability > 0.3)
# Identify dispute attractors
attractors = [
p.clause_type for p in sorted(predictions, key=lambda x: x.dispute_probability, reverse=True)[:3]
]
# Relevant triggers
relevant_triggers = self._identify_relevant_triggers(clause_types)
# Economic sensitivity
economic_clauses = ["payment", "termination", "force_majeure", "limitation_liability"]
economic_sensitivity = sum(
1 for p in predictions if p.clause_type in economic_clauses
) / max(1, len(predictions))
return DisputeCartography(
contract_id=contract_id,
total_dispute_probability=round(total_prob, 3),
high_risk_clause_count=high_risk_count,
clause_predictions=predictions,
clause_interactions=interactions,
dispute_attractors=attractors,
relevant_triggers=relevant_triggers,
economic_sensitivity=round(economic_sensitivity, 3)
)
def _extract_clauses(self, text: str) -> List[Dict[str, Any]]:
"""Extract and classify clauses from text."""
clauses = []
text_lower = text.lower()
# Simple extraction by section headers
sections = re.split(r'\n\s*\d+[\.\)]\s+|\n\n+(?=[A-Z])', text)
for i, section in enumerate(sections):
if len(section) < 50:
continue
clause_type = self._classify_clause_type(section)
clauses.append({
"index": i,
"text": section[:500],
"type": clause_type,
"length": len(section)
})
return clauses
def _classify_clause_type(self, text: str) -> str:
"""Classify clause type from text."""
text_lower = text.lower()
type_keywords = {
"indemnification": ["indemnify", "hold harmless"],
"limitation_liability": ["limitation of liability", "liability shall not exceed"],
"force_majeure": ["force majeure", "act of god"],
"termination": ["termination", "terminate"],
"ip_assignment": ["intellectual property", "work product"],
"non_compete": ["non-compete", "competitive"],
"warranty": ["warranty", "represents and warrants"],
"payment": ["payment", "invoice", "fees"],
"confidentiality": ["confidential", "non-disclosure"],
"data_protection": ["personal data", "privacy"],
}
for clause_type, keywords in type_keywords.items():
if any(kw in text_lower for kw in keywords):
return clause_type
return "other"
def _predict_clause_dispute(
self,
clause: Dict[str, Any],
party_context: Dict[str, Any] = None
) -> DisputePrediction:
"""Predict dispute probability for a single clause."""
clause_type = clause.get("type", "other")
text = clause.get("text", "")
# Base rate from history
base_rate = self.historical_dispute_rates.get(clause_type, 0.05)
# Ambiguity factor
ambiguity = self._calculate_ambiguity(text)
# Materiality (proxy: clause length and specificity)
materiality = min(1.0, len(text) / 1000)
# Party incentive alignment (would need context for real analysis)
incentive_alignment = 0 # Neutral
# Trigger sensitivity
trigger_sensitivity = 0
for trigger, impacts in self.trigger_impacts.items():
if clause_type in impacts:
trigger_sensitivity = max(trigger_sensitivity, impacts[clause_type])
# Calculate probability
probability = base_rate * (1 + ambiguity) * (1 + materiality * 0.5) * (1 + trigger_sensitivity)
probability = min(0.95, probability)
# Likely triggers
likely_triggers = [
trigger for trigger, impacts in self.trigger_impacts.items()
if clause_type in impacts
]
# Timeframe based on probability
if probability > 0.5:
timeframe = "near"
elif probability > 0.2:
timeframe = "medium"
else:
timeframe = "distant"
return DisputePrediction(
clause_text=text[:200] + "..." if len(text) > 200 else text,
clause_type=clause_type,
dispute_probability=round(probability, 3),
confidence=0.7, # Fixed for now
ambiguity_score=round(ambiguity, 3),
materiality_score=round(materiality, 3),
party_incentive_alignment=incentive_alignment,
trigger_sensitivity=round(trigger_sensitivity, 3),
likely_trigger_events=likely_triggers,
expected_timeframe=timeframe,
likely_outcome="settlement" if probability < 0.4 else "litigation"
)
def _calculate_ambiguity(self, text: str) -> float:
"""Calculate ambiguity score for clause text."""
text_lower = text.lower()
ambiguous_terms = [
"reasonable", "material", "substantial", "appropriate",
"best efforts", "timely", "prompt"
]
count = sum(text_lower.count(term) for term in ambiguous_terms)
word_count = len(text.split())
return min(1.0, count / max(1, word_count / 20))
def _find_interactions(
self,
clause_types: List[str],
predictions: List[DisputePrediction]
) -> List[Dict[str, Any]]:
"""Find clause interactions that amplify risk."""
interactions = []
for types, amplifier, description in self.interaction_amplifiers:
if all(t in clause_types for t in types):
interactions.append({
"clauses": types,
"amplifier": amplifier,
"description": description
})
return interactions
def _identify_relevant_triggers(self, clause_types: List[str]) -> List[Dict[str, Any]]:
"""Identify which trigger events are relevant to this contract."""
triggers = []
for trigger, impacts in self.trigger_impacts.items():
affected_clauses = [ct for ct in clause_types if ct in impacts]
if affected_clauses:
triggers.append({
"trigger": trigger,
"affected_clauses": affected_clauses,
"max_impact": max(impacts.get(ct, 0) for ct in affected_clauses)
})
return sorted(triggers, key=lambda t: t["max_impact"], reverse=True)
# Module instances
ambiguity_tracker = StrategicAmbiguityTracker()
dispute_predictor = DisputePredictor()
