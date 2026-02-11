"""
Frontier V: Jurisprudential Strain Detection
Where is the law itself under stress?
Frontier VI: Inferring Unstated Social Structures
What does the contract reveal about the relationship it governs?
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum
import re
from src.logger import setup_logger
logger = setup_logger("frontier_strain")
# ==================== FRONTIER V: JURISPRUDENTIAL STRAIN ====================
class StrainType(str, Enum):
DOCTRINAL_GAP = "doctrinal_gap"
ENFORCEMENT_INCONSISTENCY = "enforcement_inconsistency"
LEGISLATIVE_PRESSURE = "legislative_pressure"
TECHNOLOGY_OUTPACE = "technology_outpace"
CROSS_JURISDICTION_CONFLICT = "cross_jurisdiction_conflict"
@dataclass
class LegalStrain:
"""A point of stress in legal doctrine."""
strain_type: StrainType
doctrine_area: str
jurisdiction: str
description: str
severity: float # 0-1
# Evidence
conflicting_authorities: List[str]
enforcement_rate: Optional[float] # How often enforced as written
# Prediction
likely_resolution: str
resolution_timeframe: str # "near" (<2 years), "medium" (2-5), "distant" (5+)
def to_dict(self) -> Dict[str, Any]:
d = asdict(self)
d["strain_type"] = self.strain_type.value
return d
@dataclass
class StrainAnalysis:
"""Analysis of legal strain points in a contract."""
contract_id: str
jurisdiction: str
# Identified strains
strain_points: List[LegalStrain]
total_strain_score: float
# Clause-level risk from strain
unstable_clauses: List[Dict[str, Any]]
# Predictions
likely_future_changes: List[str]
litigation_landmines: List[str]
def to_dict(self) -> Dict[str, Any]:
d = asdict(self)
d["strain_points"] = [sp.to_dict() for sp in self.strain_points]
return d
class JurisprudentialStrainDetector:
"""
Detects where law is under stress - where doctrines are straining
against new realities and change is likely.
"""
def __init__(self):
# Known strain points by jurisdiction
self.known_strains = self._initialize_strain_database()
# Clause patterns that touch strain points
self.strain_touching_patterns = {
"ai_liability": [
r"artificial intelligence", r"machine learning", r"automated decision",
r"algorithm", r"neural network"
],
"data_sovereignty": [
r"data localization", r"cross-border transfer", r"data residency",
r"cloud storage", r"server location"
],
"gig_economy": [
r"independent contractor", r"not an employee", r"self-employed",
r"work schedule flexibility"
],
"smart_contracts": [
r"smart contract", r"blockchain", r"decentralized", r"token",
r"cryptocurrency"
],
"force_majeure_pandemic": [
r"pandemic", r"epidemic", r"public health emergency",
r"government shutdown"
],
}
def _initialize_strain_database(self) -> Dict[str, List[LegalStrain]]:
"""Initialize database of known legal strain points."""
return {
"US": [
LegalStrain(
strain_type=StrainType.LEGISLATIVE_PRESSURE,
doctrine_area="Non-compete Agreements",
jurisdiction="US",
description="FTC ban and state-level restrictions creating patchwork",
severity=0.8,
conflicting_authorities=["FTC Rule", "State laws (CA, MN, OK)", "Employer lobbying"],
enforcement_rate=0.4,
likely_resolution="Federal preemption or continued fragmentation",
resolution_timeframe="near"
),
LegalStrain(
strain_type=StrainType.TECHNOLOGY_OUTPACE,
doctrine_area="AI Liability",
jurisdiction="US",
description="No clear doctrine for AI-caused harms",
severity=0.7,
conflicting_authorities=["Product liability analogies", "Service liability analogies"],
enforcement_rate=None,
likely_resolution="New legislation or landmark case",
resolution_timeframe="medium"
),
],
"EU": [
LegalStrain(
strain_type=StrainType.CROSS_JURISDICTION_CONFLICT,
doctrine_area="Data Transfers",
jurisdiction="EU",
description="Schrems II aftermath - SCCs under pressure",
severity=0.75,
conflicting_authorities=["GDPR", "US CLOUD Act", "National security laws"],
enforcement_rate=0.3,
likely_resolution="New transatlantic framework",
resolution_timeframe="near"
),
LegalStrain(
strain_type=StrainType.TECHNOLOGY_OUTPACE,
doctrine_area="AI Act Compliance",
jurisdiction="EU",
description="New AI Act creating implementation uncertainty",
severity=0.6,
conflicting_authorities=["AI Act", "Member state interpretations"],
enforcement_rate=None,
likely_resolution="Guidance and caselaw development",
resolution_timeframe="medium"
),
],
"UK": [
LegalStrain(
strain_type=StrainType.DOCTRINAL_GAP,
doctrine_area="Smart Contract Enforceability",
jurisdiction="UK",
description="Treatment of code-as-contract unclear",
severity=0.5,
conflicting_authorities=["UKJT Statement", "Traditional contract law"],
enforcement_rate=None,
likely_resolution="Caselaw development",
resolution_timeframe="medium"
),
],
}
def analyze(
self,
contract_text: str,
contract_id: str,
jurisdiction: str,
clause_types: List[str] = None
) -> StrainAnalysis:
"""
Analyze a contract for exposure to legal strain points.
"""
text_lower = contract_text.lower()
# Find which strain areas this contract touches
touched_areas = []
for area, patterns in self.strain_touching_patterns.items():
if any(re.search(p, text_lower) for p in patterns):
touched_areas.append(area)
# Get applicable strains for jurisdiction
applicable_strains = self.known_strains.get(jurisdiction, [])
# Filter to relevant strains
relevant_strains = []
for strain in applicable_strains:
# Check if strain doctrine area relates to touched areas
area_lower = strain.doctrine_area.lower()
if any(ta in area_lower or area_lower in ta for ta in touched_areas):
relevant_strains.append(strain)
# Also include high-severity strains regardless
elif strain.severity > 0.7:
relevant_strains.append(strain)
# Calculate total strain score
total_strain = sum(s.severity for s in relevant_strains)
# Identify unstable clauses
unstable = []
for area in touched_areas:
patterns = self.strain_touching_patterns.get(area, [])
for pattern in patterns:
matches = list(re.finditer(pattern, text_lower))
for match in matches[:1]: # First match only
unstable.append({
"strain_area": area,
"matched_text": match.group(),
"position": match.start(),
"concern": f"Touches unstable legal area: {area}"
})
# Generate predictions
predictions = []
landmines = []
for strain in relevant_strains:
if strain.resolution_timeframe == "near":
predictions.append(
f"Expect changes in {strain.doctrine_area} within 2 years"
)
if strain.enforcement_rate and strain.enforcement_rate < 0.5:
landmines.append(
f"{strain.doctrine_area}: clause may not be enforced as written"
)
return StrainAnalysis(
contract_id=contract_id,
jurisdiction=jurisdiction,
strain_points=relevant_strains,
total_strain_score=round(total_strain, 3),
unstable_clauses=unstable,
likely_future_changes=predictions,
litigation_landmines=landmines
)
# ==================== FRONTIER VI: SOCIAL STRUCTURES ====================
class RelationshipType(str, Enum):
PARTNERSHIP = "partnership"
SUBORDINATION = "subordination"
ARM_LENGTH = "arms_length"
DEPENDENCY = "dependency"
SURVEILLANCE = "surveillance"
TRANSACTIONAL = "transactional"
@dataclass
class SocialStructureAnalysis:
"""Analysis of the relationship encoded in a contract."""
contract_id: str
# Relationship classification
relationship_type: RelationshipType
relationship_confidence: float
# Power analysis
power_asymmetry_score: float # -1 to 1, negative = party A dominant
dominant_party: str
# Trust indicators
monitoring_intensity: float # 0-1, higher = less trust
exit_cost_asymmetry: float # -1 to 1
# Dependency analysis
dependency_direction: str # "A->B", "B->A", "mutual", "none"
dependency_strength: float
# Structural red flags
structural_concerns: List[str]
# Narrative
relationship_narrative: str
def to_dict(self) -> Dict[str, Any]:
d = asdict(self)
d["relationship_type"] = self.relationship_type.value
return d
class SocialStructureAnalyzer:
"""
Analyzes contracts to reveal the social/power structures they encode,
beyond their explicit legal terms.
"""
def __init__(self):
# Monitoring intensity indicators
self.monitoring_patterns = [
(r"shall report", 1),
(r"monthly report", 2),
(r"weekly report", 3),
(r"daily report", 4),
(r"real-time access", 5),
(r"audit rights", 2),
(r"inspection rights", 2),
(r"upon request", 1),
(r"immediate notice", 3),
]
# Power indicator patterns
self.power_a_patterns = [ # Party A has power
r"at [party a]'s sole discretion",
r"[party a] may terminate",
r"[party a] shall have the right",
r"[party a] reserves the right",
]
self.power_b_patterns = [ # Party B has power
r"at [party b]'s sole discretion",
r"[party b] may terminate",
r"[party b] shall have the right",
]
# Exit cost patterns
self.exit_patterns = [
(r"non-refundable", "high_exit_cost"),
(r"termination fee", "exit_fee"),
(r"liquidated damages", "exit_penalty"),
(r"transition assistance", "managed_exit"),
(r"wind-down period", "managed_exit"),
]
def analyze(
self,
contract_text: str,
contract_id: str,
party_a: str = "Party A",
party_b: str = "Party B"
) -> SocialStructureAnalysis:
"""
Analyze the social structure encoded in a contract.
"""
text_lower = contract_text.lower()
# Calculate monitoring intensity
monitoring_score = 0
for pattern, weight in self.monitoring_patterns:
if re.search(pattern, text_lower):
monitoring_score += weight
monitoring_intensity = min(1.0, monitoring_score / 15) # Normalized
# Analyze power distribution
power_a = self._count_power_indicators(text_lower, party_a.lower())
power_b = self._count_power_indicators(text_lower, party_b.lower())
total_power = power_a + power_b
if total_power > 0:
power_asymmetry = (power_a - power_b) / total_power
else:
power_asymmetry = 0
dominant = party_a if power_asymmetry > 0.1 else party_b if power_asymmetry < -0.1 else "balanced"
# Analyze exit costs
exit_asymmetry = self._analyze_exit_asymmetry(text_lower, party_a.lower(), party_b.lower())
# Determine relationship type
relationship_type = self._classify_relationship(
monitoring_intensity, power_asymmetry, exit_asymmetry
)
# Analyze dependency
dep_direction, dep_strength = self._analyze_dependency(
text_lower, party_a.lower(), party_b.lower()
)
# Identify structural concerns
concerns = self._identify_concerns(
monitoring_intensity, power_asymmetry, exit_asymmetry, relationship_type
)
# Generate narrative
narrative = self._generate_narrative(
relationship_type, dominant, monitoring_intensity, dep_direction
)
return SocialStructureAnalysis(
contract_id=contract_id,
relationship_type=relationship_type,
relationship_confidence=0.75, # Fixed confidence for now
power_asymmetry_score=round(power_asymmetry, 3),
dominant_party=dominant,
monitoring_intensity=round(monitoring_intensity, 3),
exit_cost_asymmetry=round(exit_asymmetry, 3),
dependency_direction=dep_direction,
dependency_strength=round(dep_strength, 3),
structural_concerns=concerns,
relationship_narrative=narrative
)
def _count_power_indicators(self, text: str, party: str) -> int:
"""Count power indicators for a party."""
count = 0
patterns = [
f"at {party}'s sole discretion",
f"{party} may terminate",
f"{party} shall have the right",
f"{party} reserves the right",
f"{party} may, in its",
f"consent of {party}",
]
for pattern in patterns:
count += len(re.findall(pattern, text))
return count
def _analyze_exit_asymmetry(self, text: str, party_a: str, party_b: str) -> float:
"""Analyze exit cost asymmetry between parties."""
a_exit_hard = 0
b_exit_hard = 0
# Look for party-specific exit obstacles
if re.search(f"{party_a}.*non-refundable", text):
b_exit_hard += 1
if re.search(f"{party_b}.*non-refundable", text):
a_exit_hard += 1
if re.search(f"{party_a}.*termination fee", text):
a_exit_hard += 1
if re.search(f"{party_b}.*termination fee", text):
b_exit_hard += 1
total = a_exit_hard + b_exit_hard
if total == 0:
return 0
return (a_exit_hard - b_exit_hard) / total
def _classify_relationship(
self,
monitoring: float,
power: float,
exit: float
) -> RelationshipType:
"""Classify the relationship type based on signals."""
if monitoring > 0.6:
return RelationshipType.SURVEILLANCE
if abs(power) > 0.5 and abs(exit) > 0.3:
return RelationshipType.SUBORDINATION
if abs(exit) > 0.5:
return RelationshipType.DEPENDENCY
if abs(power) < 0.2 and abs(exit) < 0.2:
return RelationshipType.PARTNERSHIP
return RelationshipType.ARM_LENGTH
def _analyze_dependency(
self,
text: str,
party_a: str,
party_b: str
) -> Tuple[str, float]:
"""Analyze dependency direction and strength."""
# Dependency indicators
a_depends = len(re.findall(f"{party_a}.*shall rely on.*{party_b}", text))
b_depends = len(re.findall(f"{party_b}.*shall rely on.*{party_a}", text))
# Exclusivity suggests dependency
if re.search(f"{party_a}.*exclusive", text):
b_depends += 1
if re.search(f"{party_b}.*exclusive", text):
a_depends += 1
total = a_depends + b_depends
if total == 0:
return "none", 0
strength = min(1.0, total / 5)
if a_depends > b_depends:
return "A->B", strength
elif b_depends > a_depends:
return "B->A", strength
else:
return "mutual", strength
def _identify_concerns(
self,
monitoring: float,
power: float,
exit: float,
rel_type: RelationshipType
) -> List[str]:
"""Identify structural concerns."""
concerns = []
if monitoring > 0.7:
concerns.append("Excessive monitoring suggests control relationship, not partnership")
if abs(power) > 0.6:
concerns.append("Severe power imbalance may lead to exploitation")
if abs(exit) > 0.5:
concerns.append("Asymmetric exit costs create lock-in")
if rel_type == RelationshipType.SUBORDINATION:
concerns.append("Structure nominally equal but functionally subordinating")
return concerns
def _generate_narrative(
self,
rel_type: RelationshipType,
dominant: str,
monitoring: float,
dependency: str
) -> str:
"""Generate a narrative description of the relationship."""
narratives = {
RelationshipType.PARTNERSHIP: "This contract encodes a balanced partnership with mutual obligations and shared risk.",
RelationshipType.SUBORDINATION:
f"Despite formal equality, this contract structurally subordinates one party to {dominant}.",
RelationshipType.SURVEILLANCE:
"The information rights in this agreement constitute surveillance, not governance.",
RelationshipType.DEPENDENCY:
f"This contract creates strong dependency ({dependency}); exit is costly.",
RelationshipType.ARM_LENGTH:
"This is a standard arm's-length transaction with balanced terms.",
RelationshipType.TRANSACTIONAL:
"This is a pure transaction with minimal ongoing relationship expectations.",
}
return narratives.get(rel_type, "Relationship structure unclear.")
# Module instances
strain_detector = JurisprudentialStrainDetector()
social_analyzer = SocialStructureAnalyzer()
