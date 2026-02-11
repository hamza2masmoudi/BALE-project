"""
BALE Frontier Analysis - Unified API
Master interface for all 10 frontier capabilities.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from src.frontier.core import (
corpus, ContractType, ContractMetadata, EXPECTED_CLAUSES
)
from src.frontier.silence_archaeology import (
silence_detector, archaeologist, SilenceAnalysis, ArchaeologyAnalysis
)
from src.frontier.temporal_network import (
temporal_tracker, network_analyzer, TemporalDecayAnalysis, NetworkInference
)
from src.frontier.strain_social import (
strain_detector, social_analyzer, StrainAnalysis, SocialStructureAnalysis
)
from src.frontier.ambiguity_dispute import (
ambiguity_tracker, dispute_predictor, AmbiguityAnalysis, DisputeCartography
)
from src.frontier.imagination_reflexive import (
imagination_analyzer, reflexive_monitor, ImaginationAnalysis, ReflexiveAnalysis
)
from src.logger import setup_logger
logger = setup_logger("frontier_api")
@dataclass
class FrontierAnalysisRequest:
"""Request for frontier analysis."""
contract_id: str
contract_text: str
contract_type: ContractType
jurisdiction: str
industry: str = "general"
effective_date: Optional[str] = None
parties: List[str] = None
party_a: str = "Party A"
party_b: str = "Party B"
# Analysis options
run_silence: bool = True
run_archaeology: bool = True
run_temporal: bool = True
run_network: bool = True
run_strain: bool = True
run_social: bool = True
run_ambiguity: bool = True
run_dispute: bool = True
run_imagination: bool = True
run_reflexive: bool = True
@dataclass
class ComprehensiveFrontierAnalysis:
"""Complete frontier analysis results."""
contract_id: str
analysis_timestamp: str
# Individual analyses
silence: Optional[SilenceAnalysis] = None
archaeology: Optional[ArchaeologyAnalysis] = None
temporal: Optional[TemporalDecayAnalysis] = None
network: Optional[Dict[str, NetworkInference]] = None # Per party
strain: Optional[StrainAnalysis] = None
social: Optional[SocialStructureAnalysis] = None
ambiguity: Optional[AmbiguityAnalysis] = None
dispute: Optional[DisputeCartography] = None
imagination: Optional[ImaginationAnalysis] = None
reflexive: Optional[ReflexiveAnalysis] = None
# Summary metrics
overall_frontier_risk: float = 0
critical_findings: List[str] = None
recommended_actions: List[str] = None
def to_dict(self) -> Dict[str, Any]:
d = {
"contract_id": self.contract_id,
"analysis_timestamp": self.analysis_timestamp,
"overall_frontier_risk": self.overall_frontier_risk,
"critical_findings": self.critical_findings or [],
"recommended_actions": self.recommended_actions or [],
}
if self.silence:
d["silence"] = self.silence.to_dict()
if self.archaeology:
d["archaeology"] = self.archaeology.to_dict()
if self.temporal:
d["temporal"] = self.temporal.to_dict()
if self.network:
d["network"] = {k: v.to_dict() for k, v in self.network.items()}
if self.strain:
d["strain"] = self.strain.to_dict()
if self.social:
d["social"] = self.social.to_dict()
if self.ambiguity:
d["ambiguity"] = self.ambiguity.to_dict()
if self.dispute:
d["dispute"] = self.dispute.to_dict()
if self.imagination:
d["imagination"] = self.imagination.to_dict()
if self.reflexive:
d["reflexive"] = self.reflexive.to_dict()
return d
class FrontierAnalyzer:
"""
Master analyzer that orchestrates all 10 frontier capabilities.
"""
def __init__(self):
self.analysis_count = 0
def analyze(self, request: FrontierAnalysisRequest) -> ComprehensiveFrontierAnalysis:
"""
Run comprehensive frontier analysis on a contract.
"""
logger.info(f"Starting frontier analysis for {request.contract_id}")
result = ComprehensiveFrontierAnalysis(
contract_id=request.contract_id,
analysis_timestamp=datetime.utcnow().isoformat(),
critical_findings=[],
recommended_actions=[]
)
risk_components = []
# I. Silence Detection
if request.run_silence:
result.silence = silence_detector.analyze(
request.contract_text,
request.contract_type,
request.contract_id
)
risk_components.append(result.silence.silence_score / 100)
if result.silence.silence_score > 50:
result.critical_findings.append(
f"High silence score ({result.silence.silence_score}%): "
f"{len(result.silence.likely_strategic_omissions)} strategic omissions detected"
)
result.recommended_actions.append(
"Review missing clauses: " + ", ".join(result.silence.likely_strategic_omissions[:3])
)
# II. Contract Archaeology
if request.run_archaeology:
result.archaeology = archaeologist.analyze(
request.contract_text,
request.contract_id
)
risk_components.append(1 - result.archaeology.negotiation_intensity_score)
if result.archaeology.placeholder_scars:
result.critical_findings.append(
f"Template not fully customized: {len(result.archaeology.placeholder_scars)} placeholders found"
)
result.recommended_actions.append("Replace generic placeholders with specific terms")
# III. Temporal Decay
if request.run_temporal and request.effective_date:
clause_types = self._extract_clause_types(request.contract_text)
result.temporal = temporal_tracker.analyze_decay(
request.contract_id,
request.effective_date,
request.jurisdiction,
original_risk=50, # Default; would come from main analysis
clause_types=clause_types,
industry=request.industry
)
risk_components.append(1 - result.temporal.meaning_stability_index)
if result.temporal.needs_review:
result.critical_findings.append(
f"Contract meaning has drifted: stability index {result.temporal.meaning_stability_index:.2f}"
)
result.recommended_actions.append(
f"Urgent review needed: {result.temporal.review_urgency} priority"
)
# IV. Network Inference
if request.run_network and request.parties:
result.network = {}
for party in request.parties:
entity_id = party.lower().replace(" ", "_")[:20]
result.network[party] = network_analyzer.analyze_entity(entity_id, party)
for party, inference in result.network.items():
if inference.risk_tolerance_trend == "increasing":
result.critical_findings.append(
f"{party}: Risk tolerance increasing - possible financial pressure"
)
# V. Jurisprudential Strain
if request.run_strain:
clause_types = self._extract_clause_types(request.contract_text)
result.strain = strain_detector.analyze(
request.contract_text,
request.contract_id,
request.jurisdiction,
clause_types
)
risk_components.append(min(1.0, result.strain.total_strain_score / 2))
if result.strain.litigation_landmines:
result.critical_findings.append(
f"Legal landmines detected: {', '.join(result.strain.litigation_landmines[:2])}"
)
# VI. Social Structure
if request.run_social:
result.social = social_analyzer.analyze(
request.contract_text,
request.contract_id,
request.party_a,
request.party_b
)
if abs(result.social.power_asymmetry_score) > 0.5:
result.critical_findings.append(
f"Severe power imbalance: {result.social.dominant_party} dominates"
)
result.recommended_actions.append("Consider rebalancing terms")
for concern in result.social.structural_concerns:
result.critical_findings.append(f"Structure: {concern}")
# VII. Strategic Ambiguity
if request.run_ambiguity:
result.ambiguity = ambiguity_tracker.analyze_contract(
request.contract_text,
request.contract_id,
request.jurisdiction,
request.industry
)
risk_components.append(result.ambiguity.interpretation_risk_score / 100)
if result.ambiguity.interpretation_risk_score > 50:
result.critical_findings.append(
f"High ambiguity risk: {len(result.ambiguity.likely_intentional)} intentional vague terms"
)
# VIII. Dispute Cartography
if request.run_dispute:
result.dispute = dispute_predictor.predict_disputes(
request.contract_text,
request.contract_id
)
risk_components.append(result.dispute.total_dispute_probability)
high_risk_clauses = [
p for p in result.dispute.clause_predictions if p.dispute_probability > 0.4
]
if high_risk_clauses:
result.critical_findings.append(
f"High dispute risk: {len(high_risk_clauses)} clauses likely to be contested"
)
result.recommended_actions.append(
f"Focus negotiation on: {', '.join(result.dispute.dispute_attractors[:3])}"
)
# IX. Legal Imagination
if request.run_imagination:
result.imagination = imagination_analyzer.analyze(
request.contract_text,
request.contract_id,
request.jurisdiction
)
risk_components.append(result.imagination.total_gap_exposure)
if result.imagination.needs_pioneering_attention:
result.critical_findings.append(
f"Legal frontier: {len(result.imagination.imagination_gaps)} areas where doctrine is unclear"
)
result.recommended_actions.append(
"Seek specialized counsel for novel legal areas"
)
# X. Reflexive Effects
if request.run_reflexive:
result.reflexive = reflexive_monitor.analyze_reflexive_effects()
for alert in result.reflexive.alerts:
result.critical_findings.append(alert)
# Calculate overall frontier risk
if risk_components:
result.overall_frontier_risk = round(
sum(risk_components) / len(risk_components) * 100, 2
)
# Track for reflexive analysis
self.analysis_count += 1
reflexive_monitor.record_analysis(
request.contract_id,
int(result.overall_frontier_risk),
{}, # Would include clause fingerprints
result.analysis_timestamp
)
logger.info(
f"Frontier analysis complete for {request.contract_id}: "
f"risk={result.overall_frontier_risk}%, "
f"findings={len(result.critical_findings)}"
)
return result
def _extract_clause_types(self, text: str) -> List[str]:
"""Extract clause types from contract text."""
text_lower = text.lower()
types = []
type_keywords = {
"force_majeure": ["force majeure", "act of god"],
"limitation_liability": ["limitation of liability"],
"indemnification": ["indemnify", "hold harmless"],
"termination": ["termination", "terminate"],
"confidentiality": ["confidential"],
"ip_assignment": ["intellectual property"],
"non_compete": ["non-compete", "competitive"],
"data_protection": ["personal data", "gdpr"],
}
for clause_type, keywords in type_keywords.items():
if any(kw in text_lower for kw in keywords):
types.append(clause_type)
return types
# Convenience functions
frontier_analyzer = FrontierAnalyzer()
def analyze_contract_frontiers(
contract_text: str,
contract_type: str = "unknown",
jurisdiction: str = "INTERNATIONAL",
contract_id: str = None,
**kwargs
) -> ComprehensiveFrontierAnalysis:
"""
Convenience function for full frontier analysis.
Usage:
from src.frontier import analyze_contract_frontiers
result = analyze_contract_frontiers(
contract_text="...",
contract_type="nda",
jurisdiction="UK"
)
print(result.critical_findings)
"""
from uuid import uuid4
try:
ct = ContractType(contract_type.lower())
except ValueError:
ct = ContractType.UNKNOWN
request = FrontierAnalysisRequest(
contract_id=contract_id or str(uuid4()),
contract_text=contract_text,
contract_type=ct,
jurisdiction=jurisdiction,
**kwargs
)
return frontier_analyzer.analyze(request)
# Export all
__all__ = [
"frontier_analyzer",
"FrontierAnalyzer",
"FrontierAnalysisRequest",
"ComprehensiveFrontierAnalysis",
"analyze_contract_frontiers",
# Individual analyzers
"silence_detector",
"archaeologist", "temporal_tracker",
"network_analyzer",
"strain_detector",
"social_analyzer",
"ambiguity_tracker",
"dispute_predictor",
"imagination_analyzer",
"reflexive_monitor",
]
