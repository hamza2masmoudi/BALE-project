"""
BALE Novel Frontier Detection Algorithms
These are the core IP differentiators:
1. Bayesian Silence Detection - Information theoretic surprise for missing clauses
2. Obligation Graph Analysis - Power asymmetry via graph centrality
3. Temporal Decay Detection - Legal regime change impact modeling
4. Deontic Strain Detection - Logical conflict detection
Author: BALE Project
"""
import json
import math
import os
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
from src.logger import setup_logger
from src.ontology import (
ClauseCategory, Jurisdiction, CLAUSE_EXPECTATIONS,
LEGAL_REGIME_CHANGES,
ObligationType
)
logger = setup_logger("novel_algorithms")
# =============================================================================
# 1. BAYESIAN SILENCE DETECTOR
# =============================================================================
@dataclass
class SilenceResult:
"""Result of silence detection."""
missing_clause: str
surprise_score: float # Information theoretic surprise (bits)
expected_probability: float # P(clause | context)
severity: str # low, medium, high, critical
recommendation: str
class BayesianSilenceDetector:
"""
Novel Algorithm: Bayesian Missing Clause Detection
Uses learned clause co-occurrence patterns from CUAD to compute
"surprise" when expected clauses are absent.
Novelty: Information-theoretic quantification of clause absence significance.
Formula: surprise(C₁|C₂...Cₙ) = -log₂(1 - P(C₁|C₂...Cₙ))
High surprise = unusual absence = potential risk
"""
def __init__(self, cooccurrence_path: str = "data/processed/clause_cooccurrence.json"):
self.cooccurrence: Dict[str, Dict[str, int]] = {}
self.total_contracts: int = 510 # From CUAD
self.clause_frequencies: Dict[str, int] = {}
if os.path.exists(cooccurrence_path):
self._load_cooccurrence(cooccurrence_path)
logger.info(f"Loaded co-occurrence matrix with {len(self.cooccurrence)} categories")
else:
logger.warning(f"Co-occurrence file not found: {cooccurrence_path}")
def _load_cooccurrence(self, path: str):
"""Load pre-computed co-occurrence matrix."""
with open(path) as f:
self.cooccurrence = json.load(f)
# Compute marginal frequencies
for cat, co_cats in self.cooccurrence.items():
self.clause_frequencies[cat] = sum(co_cats.values()) // len(co_cats) if co_cats else 0
def conditional_probability(self, target: str, present_clauses: Set[str]) -> float:
"""
Compute P(target_clause | present_clauses) using co-occurrence.
Uses maximum likelihood estimate with Laplace smoothing.
"""
if not present_clauses or target not in self.cooccurrence:
# Fall back to marginal probability
return self.clause_frequencies.get(target, 50) / self.total_contracts
# Average conditional probability given each present clause
probs = []
for present in present_clauses:
if present in self.cooccurrence:
co_count = self.cooccurrence[present].get(target, 0)
total = sum(self.cooccurrence[present].values())
if total > 0:
# Laplace smoothing
prob = (co_count + 1) / (total + len(self.cooccurrence))
probs.append(prob)
if probs:
return sum(probs) / len(probs)
return 0.1 # Default low probability
def surprise_score(self, target: str, present_clauses: Set[str]) -> float:
"""
Compute information-theoretic surprise for missing clause.
Surprise = -log₂(1 - P(clause_present | context))
Higher surprise = more unusual absence.
"""
prob = self.conditional_probability(target, present_clauses)
# Clamp probability to avoid log(0)
prob = min(max(prob, 0.01), 0.99)
# Surprise for ABSENCE: how surprising is it that this clause is missing?
surprise = -math.log2(1 - prob)
return surprise
def detect_silences(
self, contract_type: str, present_clauses: Set[str],
top_k: int = 5
) -> List[SilenceResult]:
"""
Detect missing clauses with significance scores.
Returns top-k most surprising absences.
"""
# Get expected clauses for contract type
expected = get_expected_clauses(contract_type)
# Add clauses that co-occur frequently with present ones
for present in present_clauses:
if present in self.cooccurrence:
for co_clause, count in self.cooccurrence[present].items():
if count > 100: # High co-occurrence threshold
expected.add(co_clause)
# Find missing clauses
missing = expected - present_clauses
# Score each missing clause
scored = []
for clause in missing:
surprise = self.surprise_score(clause, present_clauses)
prob = self.conditional_probability(clause, present_clauses)
# Determine severity
if surprise > 3:
severity = "critical"
elif surprise > 2:
severity = "high"
elif surprise > 1:
severity = "medium"
else:
severity = "low"
scored.append(SilenceResult(
missing_clause=clause,
surprise_score=surprise,
expected_probability=prob,
severity=severity,
recommendation=self._get_recommendation(clause, severity)
))
# Sort by surprise (descending)
scored.sort(key=lambda x: -x.surprise_score)
return scored[:top_k]
def _get_recommendation(self, clause: str, severity: str) -> str:
"""Generate recommendation for missing clause."""
recommendations = {
"liability_cap": "Add a mutual limitation of liability clause with reasonable cap",
"indemnification": "Include indemnification provisions to allocate risk",
"confidentiality": "Add confidentiality obligations to protect sensitive information",
"termination": "Include termination clauses for both parties",
"governing_law": "Specify governing law and jurisdiction",
"ip_ownership": "Clarify intellectual property ownership and licenses",
"warranty": "Include appropriate warranties and disclaimers",
"insurance": "Consider requiring adequate insurance coverage",
"audit_rights": "Add audit rights for compliance verification",
"force_majeure": "Include force majeure provisions for unforeseen events",
}
base = recommendations.get(clause, f"Consider adding {clause.replace('_', ' ')} provisions")
if severity == "critical":
return f"URGENT: {base}"
return base
def get_expected_clauses(contract_type: str) -> Set[str]:
"""Get expected clause categories for contract type."""
type_lower = contract_type.lower()
# Map ClauseCategory enum to strings
expected_set = set()
for cat in CLAUSE_EXPECTATIONS.get(type_lower, set()):
expected_set.add(cat.value)
# Also return common defaults
common = {"governing_law", "termination", "notice"}
return expected_set.union(common)
# =============================================================================
# 2. OBLIGATION GRAPH POWER ANALYZER
# =============================================================================
@dataclass
class ObligationEdge:
"""Directed edge in obligation graph."""
obligor: str
beneficiary: str
clause_type: str
severity: float # 0-1 weight
@dataclass
class PowerAnalysisResult:
"""Result of power asymmetry analysis."""
asymmetry_score: float # 0-1, higher = more imbalanced
favored_party: str
obligation_counts: Dict[str, int] # party -> obligation count
power_scores: Dict[str, float] # party -> power score
imbalanced_clauses: List[str]
recommendation: str
class ObligationGraphAnalyzer:
"""
Novel Algorithm: Power Asymmetry via Obligation Graph Analysis
Builds directed graph where:
- Nodes = Parties
- Edges = Obligations (A → B means A owes obligation to B)
- Edge weights = Severity/impact of obligation
Measures asymmetry using weighted in-degree centrality.
Novelty: Graph-theoretic quantification of contractual power imbalance.
"""
# Clause type to severity weight
CLAUSE_SEVERITY = {
"indemnification": 0.9,
"liability_uncapped": 1.0,
"liability_cap": 0.3,
"warranty": 0.5,
"confidentiality": 0.4,
"non_compete": 0.8,
"non_solicitation": 0.6,
"termination_convenience": 0.7,
"insurance": 0.4,
"audit_rights": 0.3,
"exclusivity": 0.7,
"ip_ownership": 0.6,
}
def __init__(self):
self.edges: List[ObligationEdge] = []
def add_obligation(self, obligor: str, beneficiary: str, clause_type: str):
"""Add obligation edge to graph."""
severity = self.CLAUSE_SEVERITY.get(clause_type, 0.5)
self.edges.append(ObligationEdge(
obligor=obligor,
beneficiary=beneficiary,
clause_type=clause_type,
severity=severity
))
def from_clause_analysis(self, clauses: List[Dict], parties: List[str]):
"""
Build obligation graph from clause analysis results.
Each clause should have:
- category: clause type
- who_benefits: party name
"""
if len(parties) < 2:
parties = ["party_a", "party_b"]
for clause in clauses:
category = clause.get("category", clause.get("clause_type", ""))
beneficiary = clause.get("who_benefits", clause.get("party_favored", ""))
# Determine obligor (opposite of beneficiary)
if beneficiary == parties[0]:
obligor = parties[1] if len(parties) > 1 else "party_b"
elif beneficiary == parties[1] if len(parties) > 1 else beneficiary == "party_b":
obligor = parties[0]
else:
# Assign based on clause type defaults
if category in ["indemnification", "warranty", "confidentiality"]:
obligor = parties[1] if len(parties) > 1 else "party_b" # Typically vendor
beneficiary = parties[0] # Typically customer
else:
continue
self.add_obligation(obligor, beneficiary, category)
def analyze(self) -> PowerAnalysisResult:
"""
Compute power asymmetry metrics.
Power score = sum of weighted in-degrees
Asymmetry = |power(A) - power(B)| / max(power(A), power(B))
"""
# Compute weighted in-degrees (who receives obligations)
power_scores: Dict[str, float] = defaultdict(float)
obligation_counts: Dict[str, int] = defaultdict(int)
for edge in self.edges:
power_scores[edge.beneficiary] += edge.severity
obligation_counts[edge.obligor] += 1
if not power_scores:
return PowerAnalysisResult(
asymmetry_score=0.0,
favored_party="balanced",
obligation_counts=dict(obligation_counts),
power_scores=dict(power_scores),
imbalanced_clauses=[],
recommendation="No obligations identified for analysis"
)
# Find most powerful party
parties = list(power_scores.keys())
if len(parties) == 1:
favored = parties[0]
asymmetry = 1.0
else:
sorted_parties = sorted(power_scores.items(), key=lambda x: -x[1])
favored = sorted_parties[0][0]
top_power = sorted_parties[0][1]
second_power = sorted_parties[1][1] if len(sorted_parties) > 1 else 0
if top_power > 0:
asymmetry = (top_power - second_power) / top_power
else:
asymmetry = 0.0
# Find most imbalanced clauses
imbalanced = []
for edge in self.edges:
if edge.severity >= 0.7 and edge.beneficiary == favored:
imbalanced.append(edge.clause_type)
# Generate recommendation
if asymmetry > 0.7:
rec = f"Contract heavily favors {favored}. Negotiate rebalancing on: {', '.join(imbalanced[:3])}"
elif asymmetry > 0.4:
rec = f"Moderate imbalance toward {favored}. Review: {', '.join(imbalanced[:2])}"
else:
rec = "Contract appears reasonably balanced"
return PowerAnalysisResult(
asymmetry_score=asymmetry,
favored_party=favored,
obligation_counts=dict(obligation_counts),
power_scores=dict(power_scores),
imbalanced_clauses=imbalanced,
recommendation=rec
)
def reset(self):
"""Clear the graph for new analysis."""
self.edges = []
# =============================================================================
# 3. TEMPORAL DECAY DETECTOR
# =============================================================================
@dataclass
class TemporalIssue:
"""Issue caused by temporal decay."""
clause_category: str
regime_change: str
effective_date: str
impact_description: str
risk_increase: float
@dataclass
class TemporalDecayResult:
"""Result of temporal decay analysis."""
contract_date: str
years_old: float
decay_score: float # 0-100
affected_clauses: List[TemporalIssue]
critical_changes: List[str]
recommendation: str
class TemporalDecayDetector:
"""
Novel Algorithm: Legal Regime Change Impact Modeling
Identifies how legal changes since contract signing affect clause validity.
Maintains database of:
- Regulatory changes (GDPR, CCPA, etc.)
- Case law shifts
- Market practice evolution
Novelty: Systematic temporal risk quantification for contracts.
"""
def __init__(self):
self.regime_changes = LEGAL_REGIME_CHANGES
def analyze(
self, contract_date: str, jurisdiction: str,
present_clauses: Set[str]
) -> TemporalDecayResult:
"""
Analyze temporal decay for a contract.
Args:
contract_date: ISO format date string (YYYY-MM-DD)
jurisdiction: Jurisdiction code (e.g., "US-CA", "EU")
present_clauses: Set of clause categories in contract
"""
try:
contract_dt = datetime.fromisoformat(contract_date.split("T")[0])
except (ValueError, AttributeError):
contract_dt = datetime(2020, 1, 1) # Default
today = datetime.now()
years_old = (today - contract_dt).days / 365.25
# Map jurisdiction string to enum
jurisdiction_enum = self._parse_jurisdiction(jurisdiction)
affected = []
total_impact = 0.0
critical_changes = []
for change in self.regime_changes:
change_date = datetime.fromisoformat(change["effective_date"])
# Check if change happened after contract was signed
if contract_dt < change_date <= today:
# Check if jurisdiction applies
matching_jurisdictions = [
j for j in change["jurisdictions"] if j == jurisdiction_enum or (
jurisdiction_enum == Jurisdiction.US_FEDERAL and str(j.value).startswith("US")
)
]
if matching_jurisdictions or jurisdiction_enum in change["jurisdictions"]:
# Check if any affected clauses are in contract
affected_clause_types = [
c.value for c in change["affected_clauses"]
]
for clause_cat in affected_clause_types:
if clause_cat in present_clauses or not present_clauses:
impact = change["impact_score"]
total_impact += impact
affected.append(TemporalIssue(
clause_category=clause_cat,
regime_change=change["name"],
effective_date=change["effective_date"],
impact_description=f"{change['name']} may affect {clause_cat} provisions",
risk_increase=impact
))
if impact >= 0.8:
critical_changes.append(change["name"])
# Calculate decay score (0-100)
# Base decay from age + impact from regime changes
age_decay = min(years_old * 5, 25) # Max 25% from age alone
change_decay = min(total_impact * 30, 75) # Max 75% from changes
decay_score = age_decay + change_decay
# Generate recommendation
if decay_score > 60:
rec = f"Contract is {years_old:.1f} years old with significant regulatory changes. URGENT REVIEW REQUIRED."
elif decay_score > 30:
rec = f"Contract may need updates for {', '.join(critical_changes[:2]) if critical_changes else 'recent regulatory changes'}"
else:
rec = "Contract is relatively current"
return TemporalDecayResult(
contract_date=contract_date,
years_old=years_old,
decay_score=decay_score,
affected_clauses=affected,
critical_changes=critical_changes,
recommendation=rec
)
def _parse_jurisdiction(self, jurisdiction: str) -> Jurisdiction:
"""Parse jurisdiction string to enum."""
mapping = {
"us": Jurisdiction.US_FEDERAL,
"us-ca": Jurisdiction.US_CALIFORNIA,
"us-de": Jurisdiction.US_DELAWARE,
"us-ny": Jurisdiction.US_NEW_YORK,
"uk": Jurisdiction.UK,
"eu": Jurisdiction.EU_GDPR,
"de": Jurisdiction.GERMANY,
"sg": Jurisdiction.SINGAPORE,
}
return mapping.get(jurisdiction.lower(), Jurisdiction.US_FEDERAL)
# =============================================================================
# 4. DEONTIC STRAIN DETECTOR
# =============================================================================
@dataclass
class DeonticStatement:
"""Parsed deontic statement from clause."""
agent: str
modality: ObligationType # O (obligated), F (forbidden), P (permitted)
action: str
conditions: List[str]
source_clause: str
@dataclass
class StrainConflict:
"""Detected conflict between clauses."""
clause_1: str
clause_2: str
conflict_type: str # contradiction, tension, ambiguity
description: str
severity: float # 0-1
@dataclass
class StrainResult:
"""Result of strain detection."""
conflicts: List[StrainConflict]
total_strain: float # 0-100
most_severe: Optional[StrainConflict]
recommendation: str
class DeonticStrainDetector:
"""
Novel Algorithm: Deontic Logic Conflict Detection
Models clauses as deontic statements:
- O(action): Obligated to do action
- P(action): Permitted to do action - F(action): Forbidden to do action
Detects logical conflicts:
- O(A) ∧ F(A): Must do AND forbidden
- O(A) ∧ O(¬A): Must do AND must not do
- Conditional conflicts when conditions can co-occur
Novelty: Formal logical conflict detection in contracts.
"""
# Action categories that can conflict
CONFLICTING_ACTIONS = {
"disclose": "keep_confidential",
"transfer_ip": "retain_ip",
"terminate_immediately": "provide_notice",
"share_with_third_party": "keep_exclusive",
"compete": "non_compete",
"solicit": "non_solicit",
"modify_terms": "preserve_terms",
"sublicense": "non_transferable",
}
def __init__(self):
self.statements: List[DeonticStatement] = []
def add_statement(
self, agent: str,
modality: ObligationType,
action: str,
conditions: List[str] = None,
source: str = ""
):
"""Add deontic statement from clause analysis."""
self.statements.append(DeonticStatement(
agent=agent,
modality=modality,
action=action,
conditions=conditions or [],
source_clause=source
))
def from_clauses(self, clauses: List[Dict]):
"""
Extract deontic statements from clause analyses.
Uses heuristics to identify obligations/permissions/prohibitions.
"""
for clause in clauses:
category = clause.get("category", clause.get("clause_type", ""))
text = clause.get("text", clause.get("clause_text", ""))[:500].lower()
party = clause.get("who_benefits", "party_a")
# Extract modality based on clause type and language
if "shall not" in text or "must not" in text or "prohibited" in text:
modality = ObligationType.NEGATIVE
elif "shall" in text or "must" in text or "obligated" in text:
modality = ObligationType.POSITIVE
elif "may" in text or "entitled" in text or "right to" in text:
modality = ObligationType.DISCRETIONARY
else:
modality = ObligationType.POSITIVE # Default
# Extract action based on category
actions = {
"confidentiality": "keep_confidential",
"non_compete": "non_compete",
"non_solicitation": "non_solicit",
"termination": "terminate",
"assignment": "transfer_rights",
"ip_ownership": "retain_ip" if party == "party_a" else "transfer_ip",
"indemnification": "indemnify",
"license_grant": "use_licensed_rights",
}
action = actions.get(category, category)
# Determine agent (opposite of beneficiary)
agent = "party_b" if party == "party_a" else "party_a"
self.add_statement(agent, modality, action, [], category)
def detect_conflicts(self) -> StrainResult:
"""
Detect logical conflicts between statements.
"""
conflicts = []
for i, s1 in enumerate(self.statements):
for s2 in self.statements[i+1:]:
conflict = self._check_conflict(s1, s2)
if conflict:
conflicts.append(conflict)
# Calculate total strain
if conflicts:
total_strain = sum(c.severity for c in conflicts) / len(conflicts) * 100
most_severe = max(conflicts, key=lambda x: x.severity)
else:
total_strain = 0.0
most_severe = None
# Generate recommendation
if total_strain > 50:
rec = f"HIGH STRAIN: Contract contains {len(conflicts)} logical conflicts. Legal review required."
elif total_strain > 20:
rec = f"Moderate strain: {len(conflicts)} potential conflicts detected"
else:
rec = "No significant logical conflicts detected"
return StrainResult(
conflicts=conflicts,
total_strain=total_strain,
most_severe=most_severe,
recommendation=rec
)
def _check_conflict(
self, s1: DeonticStatement, s2: DeonticStatement
) -> Optional[StrainConflict]:
"""Check if two statements conflict."""
# Same agent, conflicting actions
if s1.agent == s2.agent:
# Check for O(A) and F(A)
if (s1.modality == ObligationType.POSITIVE and s2.modality == ObligationType.NEGATIVE):
if self._actions_conflict(s1.action, s2.action):
return StrainConflict(
clause_1=s1.source_clause,
clause_2=s2.source_clause,
conflict_type="contradiction",
description=f"{s1.agent} is obligated to {s1.action} but forbidden from {s2.action}",
severity=0.9
)
# Check for action opposites
if s1.modality == ObligationType.POSITIVE and s2.modality == ObligationType.POSITIVE:
if self._actions_opposite(s1.action, s2.action):
return StrainConflict(
clause_1=s1.source_clause,
clause_2=s2.source_clause,
conflict_type="tension",
description=f"{s1.agent} must {s1.action} and {s2.action} (potentially conflicting)",
severity=0.6
)
return None
def _actions_conflict(self, a1: str, a2: str) -> bool:
"""Check if actions are the same (O(A) and F(A))."""
return a1 == a2 or a1 in a2 or a2 in a1
def _actions_opposite(self, a1: str, a2: str) -> bool:
"""Check if actions are semantic opposites."""
return (
(a1 in self.CONFLICTING_ACTIONS and self.CONFLICTING_ACTIONS[a1] == a2) or
(a2 in self.CONFLICTING_ACTIONS and self.CONFLICTING_ACTIONS[a2] == a1)
)
def reset(self):
"""Clear statements for new analysis."""
self.statements = []
# =============================================================================
# UNIFIED NOVEL ANALYSIS RUNNER
# =============================================================================
@dataclass
class NovelAnalysisResult:
"""Complete novel analysis result."""
# Silence detection
silence_score: float
missing_clauses: List[SilenceResult]
# Power analysis
power_asymmetry: float
power_result: PowerAnalysisResult
# Temporal decay
temporal_decay: float
temporal_result: TemporalDecayResult
# Strain detection
strain_score: float
strain_result: StrainResult
# Overall
combined_novel_risk: float
primary_concerns: List[str]
class NovelFrontierAnalyzer:
"""
Unified runner for all novel frontier detection algorithms.
"""
def __init__(self):
self.silence_detector = BayesianSilenceDetector()
self.power_analyzer = ObligationGraphAnalyzer()
self.temporal_detector = TemporalDecayDetector()
self.strain_detector = DeonticStrainDetector()
def analyze(
self,
contract_type: str,
present_clauses: Set[str],
clause_analyses: List[Dict],
parties: List[str],
contract_date: str,
jurisdiction: str
) -> NovelAnalysisResult:
"""
Run all novel analyses on a contract.
"""
# 1. Silence Detection
silences = self.silence_detector.detect_silences(contract_type, present_clauses)
silence_score = sum(s.surprise_score for s in silences) * 10 if silences else 0
# 2. Power Analysis
self.power_analyzer.reset()
self.power_analyzer.from_clause_analysis(clause_analyses, parties)
power_result = self.power_analyzer.analyze()
# 3. Temporal Decay
temporal_result = self.temporal_detector.analyze(
contract_date, jurisdiction, present_clauses
)
# 4. Strain Detection
self.strain_detector.reset()
self.strain_detector.from_clauses(clause_analyses)
strain_result = self.strain_detector.detect_conflicts()
# Combine scores
combined = (
min(silence_score, 100) * 0.25 +
power_result.asymmetry_score * 100 * 0.30 +
temporal_result.decay_score * 0.25 +
strain_result.total_strain * 0.20
)
# Primary concerns
concerns = []
if silence_score > 15:
concerns.append(f"Missing critical clauses: {silences[0].missing_clause if silences else 'unknown'}")
if power_result.asymmetry_score > 0.5:
concerns.append(f"Power imbalance favoring {power_result.favored_party}")
if temporal_result.decay_score > 30:
concerns.append(f"Contract affected by {temporal_result.critical_changes[0] if temporal_result.critical_changes else 'regulatory changes'}")
if strain_result.total_strain > 20:
concerns.append(f"Logical conflicts detected in clauses")
return NovelAnalysisResult(
silence_score=silence_score,
missing_clauses=silences,
power_asymmetry=power_result.asymmetry_score,
power_result=power_result,
temporal_decay=temporal_result.decay_score,
temporal_result=temporal_result,
strain_score=strain_result.total_strain,
strain_result=strain_result,
combined_novel_risk=min(combined, 100),
primary_concerns=concerns
)
# Singleton instance
novel_analyzer = NovelFrontierAnalyzer()
