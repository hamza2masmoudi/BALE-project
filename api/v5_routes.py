"""
BALE V5 Risk Analysis API Endpoint
Provides REST API for real-time risk analysis using the V5 model.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from src.inference.local_v5 import (
get_inference_engine,
RiskLevel,
RiskAnalysisResult,
ClassificationResult,
)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v5", tags=["V5 Analysis"])
class RiskAnalysisRequest(BaseModel):
"""Request for risk analysis."""
clause_text: str
context: Optional[str] = None
class ClassificationRequest(BaseModel):
"""Request for clause classification."""
clause_text: str
class ContractAnalysisRequest(BaseModel):
"""Request for full contract analysis."""
contract_text: str
contract_type: Optional[str] = "msa"
class RiskAnalysisResponse(BaseModel):
"""Response for risk analysis."""
risk_level: str
risk_score: float
reasoning: str
problems: List[str]
recommendations: List[str]
model_version: str = "V5"
class ClassificationResponse(BaseModel):
"""Response for clause classification."""
clause_type: str
confidence: float
reasoning: str
key_indicators: List[str]
model_version: str = "V5"
class ContractAnalysisResponse(BaseModel):
"""Response for full contract analysis."""
overall_risk_score: float
total_sections: int
high_risk_count: int
medium_risk_count: int
low_risk_count: int
high_risk_clauses: List[Dict[str, Any]]
classifications: List[Dict[str, Any]]
model_version: str = "V5"
@router.get("/status")
async def get_v5_status():
"""Check V5 model availability."""
engine = get_inference_engine()
available = engine.is_available()
return {
"v5_available": available,
"model": engine.MODEL_ID,
"adapter_path": engine.adapter_path,
"loaded": engine._loaded
}
@router.post("/risk", response_model=RiskAnalysisResponse)
async def analyze_risk(request: RiskAnalysisRequest):
"""
Analyze a clause for consumer risk.
Uses the V5 model to detect HIGH/MEDIUM/LOW risk with detailed reasoning.
"""
engine = get_inference_engine()
if not engine.is_available():
raise HTTPException(status_code=503, detail="V5 model not available")
result = engine.analyze_risk(request.clause_text)
return RiskAnalysisResponse(
risk_level=result.level.value,
risk_score=result.score,
reasoning=result.reasoning,
problems=result.problems,
recommendations=result.recommendations
)
@router.post("/classify", response_model=ClassificationResponse)
async def classify_clause(request: ClassificationRequest):
"""
Classify a contract clause.
Identifies clause type (indemnification, confidentiality, etc.)
"""
engine = get_inference_engine()
if not engine.is_available():
raise HTTPException(status_code=503, detail="V5 model not available")
result = engine.classify_clause(request.clause_text)
return ClassificationResponse(
clause_type=result.clause_type,
confidence=result.confidence,
reasoning=result.reasoning,
key_indicators=result.key_indicators
)
@router.post("/analyze-contract", response_model=ContractAnalysisResponse)
async def analyze_full_contract(request: ContractAnalysisRequest):
"""
Analyze an entire contract for risks.
Returns risk assessment for each section with overall score.
"""
engine = get_inference_engine()
if not engine.is_available():
raise HTTPException(status_code=503, detail="V5 model not available")
result = engine.analyze_contract(request.contract_text)
if "error" in result:
raise HTTPException(status_code=500, detail=result["error"])
return ContractAnalysisResponse(
overall_risk_score=result["overall_risk_score"],
total_sections=result["total_sections"],
high_risk_count=len(result["high_risk_clauses"]),
medium_risk_count=len(result["medium_risk_clauses"]),
low_risk_count=len(result["low_risk_clauses"]),
high_risk_clauses=result["high_risk_clauses"],
classifications=result["classifications"]
)
def register_v5_routes(app):
"""Register V5 routes with the FastAPI app."""
app.include_router(router)
# Check availability at startup
engine = get_inference_engine()
if engine.is_available():
logger.info("V5 model available, preloading...")
# Don't preload to save memory - lazy load on first request
else:
logger.warning("V5 model not available - API endpoints will return 503")
