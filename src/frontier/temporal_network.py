"""
Frontier III: Temporal Decay of Meaning
How does the legal meaning of a document change as the world shifts?
Frontier IV: Network Inference Across Parties
What can be inferred about an entity from the pattern of all its contracts?
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import statistics
from src.frontier.core import (
corpus, CorpusTracker, ContractMetadata, EntityProfile,
TemporalSnapshot
)
from src.logger import setup_logger
logger = setup_logger("frontier_temporal")
# ==================== FRONTIER III: TEMPORAL DECAY ====================
@dataclass
class DoctrineDrift:
"""Represents a shift in legal doctrine."""
doctrine_name: str
jurisdiction: str
original_interpretation: str
current_interpretation: str
shift_magnitude: float # 0-1
effective_date: str
source: str # case cite or regulation
@dataclass
class TemporalDecayAnalysis:
"""Analysis of how a contract's meaning has drifted over time."""
contract_id: str
original_date: str
analysis_date: str
time_elapsed_days: int
# Doctrine changes affecting this contract
applicable_doctrine_shifts: List[DoctrineDrift]
# Risk adjustment
original_risk_score: int
current_risk_score: int
risk_delta: int
# Clause-level decay
clause_stability: Dict[str, float] # clause_type -> stability score (0-1)
most_decayed_clauses: List[str]
# Industry benchmark drift
industry_benchmark_delta: float
# Meaning stability index
meaning_stability_index: float # 0-1, 1 = perfectly stable
# Recommendation
needs_review: bool
review_urgency: str # low, medium, high, critical
def to_dict(self) -> Dict[str, Any]:
d = asdict(self)
d["applicable_doctrine_shifts"] = [asdict(shift) for shift in self.applicable_doctrine_shifts]
return d
class TemporalDecayTracker:
"""
Tracks how legal meaning changes over time without document modification.
"""
def __init__(self):
# Known doctrine shifts (in production, this would be updated from legal feeds)
self.registered_shifts: List[DoctrineDrift] = []
# Industry benchmarks by jurisdiction
self.benchmarks: Dict[str, Dict[str, float]] = defaultdict(dict)
# Initialize with some known shifts
self._initialize_known_shifts()
def _initialize_known_shifts(self):
"""Initialize with major known doctrine shifts."""
self.registered_shifts = [
DoctrineDrift(
doctrine_name="Force Majeure - Pandemic",
jurisdiction="UK",
original_interpretation="Narrow: specific enumerated events only",
current_interpretation="Broader: pandemic-like events may qualify",
shift_magnitude=0.4,
effective_date="2020-03-01",
source="Various pandemic-era rulings"
),
DoctrineDrift(
doctrine_name="Reasonable Efforts Standard",
jurisdiction="US",
original_interpretation="Best efforts = more than commercially reasonable",
current_interpretation="Terms increasingly treated as synonymous",
shift_magnitude=0.3,
effective_date="2021-01-01",
source="Commercial contract caselaw trend"
),
DoctrineDrift(
doctrine_name="Data Protection Scope",
jurisdiction="EU",
original_interpretation="GDPR applies to EU data subjects",
current_interpretation="Extraterritorial reach expanding",
shift_magnitude=0.5,
effective_date="2022-01-01",
source="CJEU rulings and enforcement actions"
),
DoctrineDrift(
doctrine_name="Non-Compete Enforceability",
jurisdiction="US",
original_interpretation="Generally enforceable if reasonable",
current_interpretation="Increasing restrictions and bans",
shift_magnitude=0.6,
effective_date="2024-01-01",
source="FTC rule and state legislation"
),
]
def register_doctrine_shift(self, shift: DoctrineDrift):
"""Register a new doctrine shift."""
self.registered_shifts.append(shift)
logger.info(f"Registered doctrine shift: {shift.doctrine_name}")
def analyze_decay(
self,
contract_id: str,
contract_date: str,
jurisdiction: str,
original_risk: int,
clause_types: List[str],
industry: str = "general"
) -> TemporalDecayAnalysis:
"""
Analyze how a contract's meaning has decayed over time.
"""
original_dt = datetime.fromisoformat(contract_date.replace("Z", "+00:00"))
now = datetime.now()
days_elapsed = (now - original_dt).days
# Find applicable doctrine shifts
applicable_shifts = []
total_shift_impact = 0
for shift in self.registered_shifts:
shift_dt = datetime.fromisoformat(shift.effective_date)
# Only applies if shift happened after contract date
if shift_dt > original_dt and shift.jurisdiction in [jurisdiction, "ALL"]:
applicable_shifts.append(shift)
total_shift_impact += shift.shift_magnitude
# Calculate clause stability
clause_stability = {}
for clause_type in clause_types:
stability = self._calculate_clause_stability(
clause_type, jurisdiction, days_elapsed, applicable_shifts
)
clause_stability[clause_type] = stability
# Identify most decayed clauses
most_decayed = sorted(
clause_stability.items(), key=lambda x: x[1]
)[:3]
most_decayed_names = [c[0] for c in most_decayed]
# Calculate risk adjustment
risk_adjustment = int(total_shift_impact * 20) # Max ~20 points per shift
current_risk = min(100, original_risk + risk_adjustment)
# Industry benchmark delta
bench_key = f"{jurisdiction}:{industry}"
historical_bench = self.benchmarks.get(bench_key, {}).get("2020", 40)
current_bench = self.benchmarks.get(bench_key, {}).get("2024", 50)
benchmark_delta = current_bench - historical_bench
# Calculate meaning stability index
avg_stability = statistics.mean(clause_stability.values()) if clause_stability else 1.0
time_decay = max(0, 1 - (days_elapsed / 3650)) # 10-year decay
meaning_stability = (avg_stability * 0.6 + time_decay * 0.4)
# Determine review urgency
if meaning_stability < 0.3 or risk_adjustment > 30:
urgency = "critical"
elif meaning_stability < 0.5 or risk_adjustment > 20:
urgency = "high"
elif meaning_stability < 0.7 or risk_adjustment > 10:
urgency = "medium"
else:
urgency = "low"
return TemporalDecayAnalysis(
contract_id=contract_id,
original_date=contract_date,
analysis_date=now.isoformat(),
time_elapsed_days=days_elapsed,
applicable_doctrine_shifts=applicable_shifts,
original_risk_score=original_risk,
current_risk_score=current_risk,
risk_delta=risk_adjustment,
clause_stability=clause_stability,
most_decayed_clauses=most_decayed_names,
industry_benchmark_delta=benchmark_delta,
meaning_stability_index=round(meaning_stability, 3),
needs_review=urgency in ["high", "critical"],
review_urgency=urgency
)
def _calculate_clause_stability(
self,
clause_type: str,
jurisdiction: str,
days_elapsed: int,
shifts: List[DoctrineDrift]
) -> float:
"""Calculate stability score for a specific clause type."""
# Base stability decays with time
base_stability = max(0.5, 1 - (days_elapsed / 5475)) # 15-year horizon
# Reduce for applicable shifts
clause_keywords = {
"force_majeure": ["force majeure", "pandemic"],
"non_compete": ["non-compete", "enforceability"],
"data_protection": ["data protection", "gdpr"],
"liability": ["reasonable efforts", "best efforts"],
}
relevant_keywords = clause_keywords.get(clause_type, [])
for shift in shifts:
if any(kw.lower() in shift.doctrine_name.lower() for kw in relevant_keywords):
base_stability -= shift.shift_magnitude * 0.3
return max(0, min(1, base_stability))
# ==================== FRONTIER IV: NETWORK INFERENCE ====================
@dataclass class NetworkInference:
"""Inferences about an entity from its contracting patterns."""
entity_id: str
entity_name: str
# Derived insights
risk_tolerance_trend: str # increasing, decreasing, stable
risk_tolerance_magnitude: float
power_dynamics: Dict[str, float] # counterparty_type -> power score
dominant_position: str # buyer, seller, licensor, etc.
# Behavioral patterns
term_consistency_score: float # 0-1
term_drift_velocity: float # rate of change
# Strategic signals
market_positioning: List[str] # inferred strategic moves
potential_concerns: List[str]
# Relationship network
counterparty_concentration: float # 0-1, higher = fewer counterparties
repeat_counterparties: int
def to_dict(self) -> Dict[str, Any]:
return asdict(self)
@dataclass
class EntityBehavior:
"""Tracked behavior for an entity."""
liability_caps: List[float]
risk_scores: List[int]
jurisdictions: List[str]
contract_types: List[str]
counterparties: List[str]
timestamps: List[str]
class NetworkAnalyzer:
"""
Analyzes patterns across all contracts of an entity to infer
behavior, power dynamics, and strategic positioning.
"""
def __init__(self):
# Entity behavior history
self.entity_behaviors: Dict[str, EntityBehavior] = defaultdict(
lambda: EntityBehavior([], [], [], [], [], [])
)
def record_contract(
self,
entity_id: str,
entity_name: str,
counterparty: str,
liability_cap: float,
risk_score: int,
jurisdiction: str,
contract_type: str,
timestamp: str
):
"""Record a contract for an entity."""
behavior = self.entity_behaviors[entity_id]
behavior.liability_caps.append(liability_cap)
behavior.risk_scores.append(risk_score)
behavior.jurisdictions.append(jurisdiction)
behavior.contract_types.append(contract_type)
behavior.counterparties.append(counterparty)
behavior.timestamps.append(timestamp)
# Also update corpus
if entity_id not in corpus.entities:
corpus.entities[entity_id] = EntityProfile(
entity_id=entity_id,
name=entity_name
)
corpus.entities[entity_id].contract_count += 1
def analyze_entity(self, entity_id: str, entity_name: str = "") -> NetworkInference:
"""
Analyze an entity's contracting patterns.
"""
behavior = self.entity_behaviors.get(entity_id)
if not behavior or not behavior.risk_scores:
return self._empty_inference(entity_id, entity_name)
# Risk tolerance trend
trend, magnitude = self._calculate_trend(behavior.risk_scores)
# Power dynamics (based on risk scores vs counterparty types)
power_dynamics = self._calculate_power_dynamics(behavior)
# Dominant position
dominant = self._infer_dominant_position(behavior)
# Term consistency
consistency = self._calculate_consistency(behavior)
# Term drift velocity
drift = self._calculate_drift(behavior.liability_caps)
# Strategic signals
market_signals, concerns = self._infer_strategic_signals(behavior, trend)
# Counterparty analysis
unique_counterparties = set(behavior.counterparties)
concentration = 1 - (len(unique_counterparties) / len(behavior.counterparties)) if behavior.counterparties else 0
repeat = len(behavior.counterparties) - len(unique_counterparties)
return NetworkInference(
entity_id=entity_id,
entity_name=entity_name or entity_id,
risk_tolerance_trend=trend,
risk_tolerance_magnitude=round(magnitude, 3),
power_dynamics=power_dynamics,
dominant_position=dominant,
term_consistency_score=round(consistency, 3),
term_drift_velocity=round(drift, 3),
market_positioning=market_signals,
potential_concerns=concerns,
counterparty_concentration=round(concentration, 3),
repeat_counterparties=repeat
)
def _empty_inference(self, entity_id: str, name: str) -> NetworkInference:
return NetworkInference(
entity_id=entity_id,
entity_name=name,
risk_tolerance_trend="unknown",
risk_tolerance_magnitude=0,
power_dynamics={},
dominant_position="unknown",
term_consistency_score=0,
term_drift_velocity=0,
market_positioning=[],
potential_concerns=[],
counterparty_concentration=0,
repeat_counterparties=0
)
def _calculate_trend(self, values: List[int]) -> Tuple[str, float]:
"""Calculate trend direction and magnitude."""
if len(values) < 2:
return "stable", 0
# Simple linear regression
n = len(values)
x_mean = (n - 1) / 2
y_mean = sum(values) / n
numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
denominator = sum((i - x_mean) ** 2 for i in range(n))
if denominator == 0:
return "stable", 0
slope = numerator / denominator
if slope > 0.5:
return "increasing", slope
elif slope < -0.5:
return "decreasing", abs(slope)
else:
return "stable", abs(slope)
def _calculate_power_dynamics(self, behavior: EntityBehavior) -> Dict[str, float]:
"""Calculate power score by counterparty type."""
# Group by contract type
type_risks = defaultdict(list)
for ct, risk in zip(behavior.contract_types, behavior.risk_scores):
type_risks[ct].append(risk)
# Power inversely related to risk accepted
return {
ct: round(1 - (sum(risks) / len(risks) / 100), 3)
for ct, risks in type_risks.items()
}
def _infer_dominant_position(self, behavior: EntityBehavior) -> str:
"""Infer the entity's typical position."""
# Simple heuristic based on contract types
types = behavior.contract_types
if not types:
return "unknown"
buyer_types = {"vendor", "sla", "consulting"}
seller_types = {"license", "distribution"}
buyer_count = sum(1 for t in types if t.lower() in buyer_types)
seller_count = sum(1 for t in types if t.lower() in seller_types)
if buyer_count > seller_count:
return "buyer"
elif seller_count > buyer_count:
return "seller"
else:
return "balanced"
def _calculate_consistency(self, behavior: EntityBehavior) -> float:
"""Calculate how consistent the entity's terms are."""
if not behavior.liability_caps or len(behavior.liability_caps) < 2:
return 1.0
mean = statistics.mean(behavior.liability_caps)
if mean == 0:
return 1.0
stdev = statistics.stdev(behavior.liability_caps)
cv = stdev / mean # Coefficient of variation
return max(0, 1 - cv)
def _calculate_drift(self, values: List[float]) -> float:
"""Calculate rate of term drift."""
if len(values) < 2:
return 0
changes = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
return statistics.mean(changes) if changes else 0
def _infer_strategic_signals(
self, behavior: EntityBehavior,
trend: str
) -> Tuple[List[str], List[str]]:
"""Infer strategic signals and concerns."""
signals = []
concerns = []
# Trend-based signals
if trend == "increasing":
concerns.append("Increasing risk tolerance may indicate financial pressure")
elif trend == "decreasing":
signals.append("Tightening risk controls - maturing or preparing for transaction")
# Jurisdiction signals
if len(set(behavior.jurisdictions)) > 3:
signals.append("Multi-jurisdiction expansion underway")
# Counterparty signals
if len(set(behavior.counterparties)) < len(behavior.counterparties) * 0.3:
signals.append("High counterparty concentration - dependency risk")
concerns.append("Over-reliance on repeat counterparties")
return signals, concerns
# Module instances
temporal_tracker = TemporalDecayTracker()
network_analyzer = NetworkAnalyzer()
