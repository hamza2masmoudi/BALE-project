"""
BALE API - Request/Response Schemas
Pydantic models for API validation and documentation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ==================== ENUMS ====================

class Jurisdiction(str, Enum):
    FRANCE = "FRANCE"
    UK = "UK"
    US = "US"
    GERMANY = "GERMANY"
    INTERNATIONAL = "INTERNATIONAL"


class AnalysisDepth(str, Enum):
    QUICK = "quick"      # Fast, basic analysis
    STANDARD = "standard"  # Full multi-agent pipeline
    DEEP = "deep"        # Deep analysis with mock trial


class InferenceMode(str, Enum):
    LOCAL = "local"      # Ollama/vLLM
    MISTRAL = "mistral"  # Mistral API
    AUTO = "auto"        # System decides


# ==================== REQUEST SCHEMAS ====================

class AnalyzeClauseRequest(BaseModel):
    """Request to analyze a contract clause."""
    clause_text: str = Field(..., min_length=10, description="The clause text to analyze")
    jurisdiction: Jurisdiction = Field(default=Jurisdiction.INTERNATIONAL, description="Governing jurisdiction")
    depth: AnalysisDepth = Field(default=AnalysisDepth.STANDARD, description="Analysis depth level")
    inference_mode: InferenceMode = Field(default=InferenceMode.AUTO, description="LLM inference mode")
    include_harmonization: bool = Field(default=True, description="Generate a 'Golden Clause' fix")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clause_text": "The Supplier shall not be liable for any indirect, consequential, or incidental damages arising from this Agreement.",
                "jurisdiction": "UK",
                "depth": "standard",
                "inference_mode": "auto",
                "include_harmonization": True
            }
        }


class SimulateTrialRequest(BaseModel):
    """Request to simulate a mock trial."""
    clause_text: str = Field(..., min_length=10, description="The clause under dispute")
    plaintiff_position: Optional[str] = Field(None, description="Optional: Plaintiff's initial argument")
    defense_position: Optional[str] = Field(None, description="Optional: Defense's initial argument")
    jurisdiction: Jurisdiction = Field(default=Jurisdiction.INTERNATIONAL)
    inference_mode: InferenceMode = Field(default=InferenceMode.AUTO)


class ContractCreateRequest(BaseModel):
    """Request to store a contract for analysis."""
    name: str = Field(..., min_length=1, max_length=256)
    content: str = Field(..., description="Full contract text or PDF base64")
    jurisdiction: Jurisdiction = Field(default=Jurisdiction.INTERNATIONAL)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ContractUpdateRequest(BaseModel):
    """Request to update a contract."""
    name: Optional[str] = Field(None, max_length=256)
    metadata: Optional[Dict[str, Any]] = None


# ==================== RESPONSE SCHEMAS ====================

class DecisionFactorResponse(BaseModel):
    """A single decision factor in the verdict."""
    rule: str = Field(..., description="Legal rule applied")
    triggered: bool = Field(..., description="Whether this rule was triggered")
    impact: int = Field(..., description="Impact on risk score (-20 to +20)")
    evidence: str = Field(..., description="Textual evidence for this factor")
    legal_basis: Optional[str] = Field(None, description="Statute or case law citation")


class ExplainableVerdictResponse(BaseModel):
    """Full explainable verdict with decision trace."""
    risk_score: int = Field(..., ge=0, le=100, description="Litigation risk percentage")
    verdict: str = Field(..., description="PLAINTIFF_FAVOR or DEFENSE_FAVOR")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")
    
    # Decision Trace
    factors_applied: List[DecisionFactorResponse] = Field(default_factory=list)
    
    # Key Metrics
    interpretive_gap: int = Field(..., ge=0, le=100, description="Gap between legal systems")
    
    # Summaries
    civilist_summary: str = Field(..., description="Civil law interpretation summary")
    commonist_summary: str = Field(..., description="Common law interpretation summary")
    synthesis: str = Field(..., description="Synthesis of interpretations")


class HarmonizationResponse(BaseModel):
    """Suggested harmonized clause."""
    golden_clause: str = Field(..., description="The suggested improved clause")
    rationale: str = Field(..., description="Why this clause resolves the conflict")
    risk_reduction: int = Field(..., description="Estimated risk reduction in %")


class AnalysisResponse(BaseModel):
    """Full analysis response."""
    id: str = Field(..., description="Analysis ID for reference")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Core Results
    verdict: ExplainableVerdictResponse
    
    # Optional: Harmonization
    harmonization: Optional[HarmonizationResponse] = None
    
    # Raw Outputs (for debugging/transparency)
    raw_outputs: Optional[Dict[str, Any]] = Field(None, description="Raw agent outputs")
    
    # Processing Info
    processing_time_ms: int = Field(..., description="Total processing time")
    inference_mode_used: InferenceMode = Field(..., description="Which LLM backend was used")


class TrialTranscriptEntry(BaseModel):
    """Single entry in mock trial transcript."""
    speaker: str = Field(..., description="PLAINTIFF, DEFENSE, or JUDGE")
    content: str = Field(..., description="The argument or ruling")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TrialSimulationResponse(BaseModel):
    """Mock trial simulation result."""
    id: str = Field(..., description="Simulation ID")
    
    # Verdict
    final_risk: int = Field(..., ge=0, le=100)
    outcome: str = Field(..., description="PLAINTIFF_WIN, DEFENSE_WIN, or SETTLEMENT")
    
    # Transcript
    transcript: List[TrialTranscriptEntry] = Field(default_factory=list)
    
    # Decision Factors (from Judge)
    judicial_factors: Dict[str, bool] = Field(default_factory=dict)
    reasoning: str = Field(..., description="Judge's final reasoning")


class ContractResponse(BaseModel):
    """Contract resource representation."""
    id: str
    name: str
    jurisdiction: Jurisdiction
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    analysis_count: int = Field(default=0, description="Number of analyses run")
    last_risk_score: Optional[int] = Field(None, description="Most recent risk score")


class ContractListResponse(BaseModel):
    """Paginated list of contracts."""
    items: List[ContractResponse]
    total: int
    page: int
    page_size: int


# ==================== HEALTH & META ====================

class HealthResponse(BaseModel):
    """API health check response."""
    status: str = "healthy"
    version: str
    inference_local_available: bool
    inference_mistral_available: bool
    database_connected: bool
    vector_store_ready: bool


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    code: str  # e.g., "VALIDATION_ERROR", "INFERENCE_ERROR"
