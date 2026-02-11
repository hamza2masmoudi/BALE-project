"""
BALE V8 API Routes
Complete V8 analysis endpoints with explainability.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from src.logger import setup_logger
logger = setup_logger("bale_v8_api")
router = APIRouter(prefix="/v8", tags=["V8 Analysis"])
# ==================== REQUEST/RESPONSE MODELS ====================
class PartyPosition(str, Enum):
BUYER = "BUYER"
SELLER = "SELLER"
NEUTRAL = "NEUTRAL"
class ClauseAnalysisRequest(BaseModel):
"""Request for single clause analysis."""
clause_text: str = Field(..., min_length=10, description="The clause text to analyze")
party_position: PartyPosition = Field(default=PartyPosition.NEUTRAL)
contract_value: float = Field(default=1000000, ge=0)
run_specialists: bool = Field(default=True, description="Run specialist agents")
class Config:
json_schema_extra = {
"example": {
"clause_text": "Provider shall indemnify Customer from all claims arising from this Agreement.",
"party_position": "BUYER",
"contract_value": 500000,
"run_specialists": True
}
}
class ContractAnalysisRequest(BaseModel):
"""Request for full contract analysis."""
clauses: List[str] = Field(..., min_items=1, description="List of clause texts")
party_position: PartyPosition = Field(default=PartyPosition.NEUTRAL)
contract_value: float = Field(default=1000000, ge=0)
class ClauseClassificationResult(BaseModel):
"""Clause classification result."""
clause_type: str
category: str
confidence: float
class RiskAssessment(BaseModel):
"""Risk assessment result."""
risk_score: float = Field(..., ge=0, le=100)
risk_level: str
uk_risk: float
fr_risk: float
confidence: float
confidence_lower: float
confidence_upper: float
class LegalCitation(BaseModel):
"""Legal citation in analysis."""
source: str
jurisdiction: str
relevance_score: float
how_applied: str
class SpecialistAnalysis(BaseModel):
"""Specialist agent analysis."""
specialist: str
analysis: str
class LitigationPrediction(BaseModel):
"""Litigation outcome prediction."""
outcome_probabilities: Dict[str, float]
expected_costs: tuple
expected_duration_months: tuple
class ClauseAnalysisResponse(BaseModel):
"""Full clause analysis response."""
clause_id: str
clause_text: str
# Classification
classification: ClauseClassificationResult
# Risk
risk: RiskAssessment
# Problems and recommendations
problems: List[str]
recommendations: List[str]
# Citations
citations: List[LegalCitation]
# Specialists
specialist_analyses: Dict[str, str]
specialists_used: List[str]
# Litigation
litigation: LitigationPrediction
# Explainability
reasoning_steps: List[Dict]
risk_factors: List[Dict]
# Audit
analysis_time_ms: int
model_version: str
decision_hash: str
class ContractAnalysisResponse(BaseModel):
"""Full contract analysis response."""
summary: Dict[str, Any]
critical_issues: List[str]
top_recommendations: List[str]
clause_analyses: List[Dict]
# ==================== ENDPOINTS ====================
@router.get("/status")
async def get_v8_status():
"""Get V8 model and analyzer status."""
try:
from src.v8_analyzer import get_v8_analyzer
analyzer = get_v8_analyzer()
return {
"v8_available": True,
"model_version": "V8",
"clause_types": 75,
"specialist_agents": ["M&A", "DataPrivacy", "Employment", "DisputeResolution"],
"jurisdictions": ["UK", "FR"],
"features": {
"explainability": True,
"dual_jurisdiction": True,
"probabilistic_risk": True,
"citation_support": True
}
}
except Exception as e:
logger.error(f"V8 status check failed: {e}")
return {
"v8_available": False,
"error": str(e)
}
@router.post("/analyze/clause", response_model=ClauseAnalysisResponse)
async def analyze_clause(request: ClauseAnalysisRequest):
"""
Analyze a single contract clause.
Provides:
- Classification (75 clause types)
- Risk assessment (UK and FR jurisdictions)
- Problems and recommendations
- Legal citations
- Specialist analyses (M&A, GDPR, Employment, Dispute)
- Litigation prediction
- Full explainability with reasoning steps
"""
try:
from src.v8_analyzer import get_v8_analyzer, PartyPosition as PP
analyzer = get_v8_analyzer()
# Map party position
party_map = {
"BUYER": PP.BUYER,
"SELLER": PP.SELLER,
"NEUTRAL": PP.NEUTRAL
}
party = party_map.get(request.party_position.value, PP.NEUTRAL)
# Run analysis
result = analyzer.analyze_clause(
clause_text=request.clause_text,
clause_id="clause_1",
party=party,
contract_value=request.contract_value,
run_specialists=request.run_specialists
)
return ClauseAnalysisResponse(
clause_id=result.clause_id,
clause_text=result.clause_text[:500], # Truncate for response
classification=ClauseClassificationResult(
clause_type=result.clause_type,
category=result.clause_category,
confidence=result.confidence
),
risk=RiskAssessment(
risk_score=result.risk_score,
risk_level=result.risk_level,
uk_risk=result.uk_risk,
fr_risk=result.fr_risk,
confidence=result.confidence,
confidence_lower=result.confidence_lower,
confidence_upper=result.confidence_upper
),
problems=result.problems,
recommendations=result.recommendations,
citations=[
LegalCitation(
source=c["source"],
jurisdiction=c["jurisdiction"],
relevance_score=c["relevance_score"],
how_applied=c["how_applied"]
)
for c in result.citations
],
specialist_analyses=result.specialist_analyses,
specialists_used=result.specialists_used,
litigation=LitigationPrediction(
outcome_probabilities=result.outcome_probabilities,
expected_costs=result.expected_costs,
expected_duration_months=result.expected_duration_months
),
reasoning_steps=result.reasoning_steps,
risk_factors=result.risk_factors,
analysis_time_ms=result.analysis_time_ms,
model_version=result.model_version,
decision_hash=result.decision_hash
)
except Exception as e:
logger.error(f"V8 clause analysis failed: {e}")
raise HTTPException(status_code=500, detail=str(e))
@router.post("/analyze/contract", response_model=ContractAnalysisResponse)
async def analyze_contract(request: ContractAnalysisRequest):
"""
Analyze an entire contract (multiple clauses).
Provides:
- Aggregate risk assessment
- Critical issues across all clauses
- Top recommendations
- Individual clause analyses
"""
try:
from src.v8_analyzer import get_v8_analyzer, PartyPosition as PP
analyzer = get_v8_analyzer()
# Map party position
party_map = {
"BUYER": PP.BUYER,
"SELLER": PP.SELLER,
"NEUTRAL": PP.NEUTRAL
}
party = party_map.get(request.party_position.value, PP.NEUTRAL)
# Run analysis
result = analyzer.analyze_contract(
clauses=request.clauses,
party=party,
contract_value=request.contract_value
)
return ContractAnalysisResponse(
summary=result["summary"],
critical_issues=result["critical_issues"],
top_recommendations=result["top_recommendations"],
clause_analyses=result["clause_analyses"]
)
except Exception as e:
logger.error(f"V8 contract analysis failed: {e}")
raise HTTPException(status_code=500, detail=str(e))
@router.post("/classify")
async def classify_clause(clause_text: str):
"""Quick clause classification without full analysis."""
try:
from src.v8_analyzer import get_v8_analyzer
analyzer = get_v8_analyzer()
clause_type, category, confidence = analyzer.classify_clause(clause_text)
return {
"clause_type": clause_type,
"category": category,
"confidence": confidence / 100 if confidence > 1 else confidence
}
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
@router.post("/risk")
async def assess_risk(
clause_text: str,
party_position: PartyPosition = PartyPosition.NEUTRAL,
jurisdiction: str = "UK"
):
"""Quick risk assessment for a clause."""
try:
from src.v8_analyzer import get_v8_analyzer, PartyPosition as PP
from src.risk_model_v8 import get_clause_calculator
analyzer = get_v8_analyzer()
calculator = get_clause_calculator()
# Classify first
clause_type, category, _ = analyzer.classify_clause(clause_text)
# Map party
party_map = {
"BUYER": PP.BUYER,
"SELLER": PP.SELLER,
"NEUTRAL": PP.NEUTRAL
}
party = party_map.get(party_position.value, PP.NEUTRAL)
# Calculate risk
risk_data = calculator.calculate(clause_type, party, jurisdiction)
return risk_data
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
@router.get("/clause-types")
async def get_clause_types():
"""Get all 75 supported clause types."""
try:
from src.ontology.clause_ontology import CLAUSE_TYPES
return {
"count": len(CLAUSE_TYPES),
"types": [
{
"id": ct_id,
"name": ct.name,
"category": ct.category.value,
"risk_level": ct.risk_level.value,
"description": ct.description
}
for ct_id, ct in CLAUSE_TYPES.items()
]
}
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
@router.get("/legal-citations")
async def get_legal_citations():
"""Get all available legal citations."""
try:
from src.explainability_v8 import LEGAL_CITATIONS
return {
"count": len(LEGAL_CITATIONS),
"citations": [
{
"id": cit_id,
"source": cit.source,
"jurisdiction": cit.jurisdiction.value,
"authority_level": cit.authority_level,
"quote": cit.quote
}
for cit_id, cit in LEGAL_CITATIONS.items()
]
}
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
