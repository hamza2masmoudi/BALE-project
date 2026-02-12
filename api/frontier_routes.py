"""
BALE Frontier API Routes
FastAPI endpoints for frontier analysis, negotiation, and export.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from src.frontier import (
    analyze_contract_frontiers,
    FrontierAnalysisRequest,
    ContractType
)
from src.negotiation import (
    clause_negotiator,
    NegotiationPlaybook
)
from src.export import (
    legal_exporter,
    ExportConfig
)
from src.corpus import (
    corpus_storage,
    StoredAnalysis
)
from src.logger import setup_logger

logger = setup_logger("frontier_api")
router = APIRouter(prefix="/frontier", tags=["Frontier Analysis"])

# ==================== REQUEST/RESPONSE MODELS ====================

class FrontierAnalyzeRequest(BaseModel):
    """Request for frontier analysis."""
    contract_text: str = Field(..., min_length=100)
    contract_type: str = Field(default="unknown")
    jurisdiction: str = Field(default="INTERNATIONAL")
    industry: str = Field(default="general")
    effective_date: Optional[str] = None
    party_a: str = Field(default="Party A")
    party_b: str = Field(default="Party B")
    parties: List[str] = Field(default=[])
    contract_name: str = Field(default="Untitled Contract")
    # Options
    include_negotiation: bool = Field(default=True)
    your_position: str = Field(default="buyer")
    save_to_corpus: bool = Field(default=True)

class FrontierAnalyzeResponse(BaseModel):
    """Response from frontier analysis."""
    analysis_id: str
    contract_id: str
    analyzed_at: str
    # Risk
    overall_frontier_risk: float
    risk_level: str
    # Findings
    critical_findings: List[str]
    recommended_actions: List[str]
    # Frontier results
    frontiers: Dict[str, Any]
    # Negotiation (optional)
    negotiation_playbook: Optional[Dict[str, Any]] = None

class NegotiationRequest(BaseModel):
    """Request for negotiation playbook."""
    contract_text: str
    contract_id: str = Field(default="")
    jurisdiction: str = Field(default="US")
    industry: str = Field(default="technology")
    your_position: str = Field(default="buyer")

class ExportRequest(BaseModel):
    """Request for document export."""
    analysis_id: str
    format: str = Field(default="markdown")  # markdown, html, json
    include_executive_summary: bool = True
    include_risk_analysis: bool = True
    include_frontier_insights: bool = True
    include_negotiation_playbook: bool = True

class CorpusStatsResponse(BaseModel):
    """Corpus statistics."""
    total_analyses: int
    total_entities: int
    avg_risk_score: float
    risk_distribution: Dict[str, int]
    jurisdiction_distribution: Dict[str, int]
    type_distribution: Dict[str, int]

# ==================== ENDPOINTS ====================

@router.post("/analyze", response_model=FrontierAnalyzeResponse)
async def analyze_contract(
    request: FrontierAnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    Run comprehensive frontier analysis on a contract.
    Returns:
        FrontierAnalyzeResponse with all 10 frontier results and optional negotiation playbook.
    """
    analysis_id = str(uuid.uuid4())
    contract_id = str(uuid.uuid4())[:8]
    logger.info(f"Starting frontier analysis {analysis_id}")

    try:
        # Parse contract type
        try:
            ct = ContractType(request.contract_type.lower())
        except ValueError:
            ct = ContractType.UNKNOWN

        # Run frontier analysis
        frontier_request = FrontierAnalysisRequest(
            contract_id=contract_id,
            contract_text=request.contract_text,
            contract_type=ct,
            jurisdiction=request.jurisdiction,
            industry=request.industry,
            effective_date=request.effective_date,
            parties=request.parties or [request.party_a, request.party_b],
            party_a=request.party_a,
            party_b=request.party_b
        )

        frontier_result = analyze_contract_frontiers(
            contract_text=request.contract_text,
            contract_type=request.contract_type,
            jurisdiction=request.jurisdiction,
            industry=request.industry,
            effective_date=request.effective_date,
            parties=request.parties or [request.party_a, request.party_b],
            party_a=request.party_a,
            party_b=request.party_b
        )

        # Convert to dict
        frontiers_dict = frontier_result.to_dict()

        # Generate negotiation playbook if requested
        playbook_dict = None
        if request.include_negotiation:
            playbook = clause_negotiator.generate_playbook(
                contract_text=request.contract_text,
                contract_id=contract_id,
                jurisdiction=request.jurisdiction,
                industry=request.industry,
                your_position=request.your_position,
                frontier_analysis=frontiers_dict
            )
            playbook_dict = playbook.to_dict()

        # Determine risk level
        risk = frontier_result.overall_frontier_risk
        if risk < 30:
            risk_level = "low"
        elif risk < 60:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Save to corpus if requested
        if request.save_to_corpus:
            stored = StoredAnalysis(
                analysis_id=analysis_id,
                contract_id=contract_id,
                contract_name=request.contract_name,
                contract_type=request.contract_type,
                jurisdiction=request.jurisdiction,
                industry=request.industry,
                risk_score=int(risk),
                verdict_summary=f"Frontier risk: {risk:.1f}%",
                frontier_risk=risk,
                frontier_data=frontiers_dict,
                negotiation_playbook=playbook_dict or {},
                analyzed_at=datetime.utcnow().isoformat(),
                parties=request.parties or [request.party_a, request.party_b]
            )
            background_tasks.add_task(corpus_storage.store_analysis, stored)

        return FrontierAnalyzeResponse(
            analysis_id=analysis_id,
            contract_id=contract_id,
            analyzed_at=datetime.utcnow().isoformat(),
            overall_frontier_risk=risk,
            risk_level=risk_level,
            critical_findings=frontier_result.critical_findings or [],
            recommended_actions=frontier_result.recommended_actions or [],
            frontiers=frontiers_dict,
            negotiation_playbook=playbook_dict
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/negotiate")
async def generate_negotiation_playbook(request: NegotiationRequest):
    """
    Generate a negotiation playbook for a contract.
    """
    try:
        playbook = clause_negotiator.generate_playbook(
            contract_text=request.contract_text,
            contract_id=request.contract_id or str(uuid.uuid4())[:8],
            jurisdiction=request.jurisdiction,
            industry=request.industry,
            your_position=request.your_position
        )
        return playbook.to_dict()
    except Exception as e:
        logger.error(f"Negotiation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_analysis(request: ExportRequest):
    """
    Export analysis results to a document.
    """
    # Get stored analysis
    stored = corpus_storage.get_analysis(request.analysis_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Analysis not found")

    config = ExportConfig(
        format=request.format,
        include_executive_summary=request.include_executive_summary,
        include_risk_analysis=request.include_risk_analysis,
        include_frontier_insights=request.include_frontier_insights,
        include_negotiation_playbook=request.include_negotiation_playbook
    )

    try:
        document = legal_exporter.generate_memo(
            analysis_result={
                "contract_id": stored.contract_id,
                "contract_name": stored.contract_name,
                "jurisdiction": stored.jurisdiction,
                "risk_score": stored.risk_score,
                "verdict": {"summary": stored.verdict_summary}
            },
            frontier_result=stored.frontier_data,
            negotiation_playbook=stored.negotiation_playbook,
            config=config
        )
        return {
            "format": request.format,
            "content": document,
            "analysis_id": request.analysis_id
        }
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Get a stored analysis by ID.
    """
    stored = corpus_storage.get_analysis(analysis_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return stored.to_dict()


@router.get("/analyses")
async def list_analyses(
    limit: int = 50,
    contract_type: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    min_risk: Optional[int] = None
):
    """
    List stored analyses with optional filters.
    """
    analyses = corpus_storage.list_analyses(
        limit=limit,
        contract_type=contract_type,
        jurisdiction=jurisdiction,
        min_risk=min_risk
    )
    return [a.to_dict() for a in analyses]


@router.get("/entities")
async def list_entities(limit: int = 50):
    """
    List entity profiles from the corpus.
    """
    from src.corpus.storage import EntityProfileRecord
    entities = corpus_storage.list_entities(limit=limit)
    return [e.__dict__ for e in entities]


@router.get("/entity/{entity_id}")
async def get_entity(entity_id: str):
    """
    Get an entity profile.
    """
    entity = corpus_storage.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity.__dict__


@router.get("/stats", response_model=CorpusStatsResponse)
async def get_corpus_stats():
    """
    Get corpus-wide statistics.
    """
    return corpus_storage.get_corpus_stats()


@router.get("/benchmarks")
async def get_market_benchmarks():
    """
    Get available market benchmarks for clause negotiation.
    """
    from src.negotiation import MARKET_BENCHMARKS
    return {
        key: {
            "clause_type": b.clause_type,
            "jurisdiction": b.jurisdiction,
            "industry": b.industry,
            "typical_cap_multiplier": b.typical_cap_multiplier,
            "mutual_rate": b.mutual_rate,
            "standard_language": b.standard_language[:100] + "..."
        }
        for key, b in MARKET_BENCHMARKS.items()
    }


# ==================== V11 INNOVATION ENDPOINTS ====================

class V11AnalyzeRequest(BaseModel):
    """Request for V11 analysis with all innovations."""
    contract_text: str = Field(..., min_length=50)
    contract_type: str = Field(default="MSA")
    contract_name: str = Field(default="Untitled Contract")
    # V11 innovation toggles
    use_semantic_chunking: bool = Field(default=True)
    suggest_rewrites: bool = Field(default=True)
    simulate_risk: bool = Field(default=True)
    corpus_compare: bool = Field(default=True)

class V11AnalyzeResponse(BaseModel):
    """Response from V11 analysis."""
    # Metadata
    engine_version: str
    contract_type: str
    total_clauses: int
    analysis_time_ms: int
    # Overall
    overall_risk_score: float
    risk_level: str
    executive_summary: str
    # Classifications with calibration
    classifications: List[Dict[str, Any]]
    # Graph analysis
    graph_analysis: Dict[str, Any]
    # Power analysis
    power_analysis: Dict[str, Any]
    # Dispute prediction
    dispute_prediction: Dict[str, Any]
    # V11 Innovations
    suggested_rewrites: Optional[List[Dict[str, Any]]] = None
    risk_simulation: Optional[Dict[str, Any]] = None
    corpus_comparison: Optional[Dict[str, Any]] = None

@router.post("/v11-analyze", response_model=V11AnalyzeResponse)
async def analyze_contract_v11(request: V11AnalyzeRequest):
    """
    Run V11 pipeline with all innovations:
    - Semantic chunking
    - Confidence calibration
    - Clause rewrite suggestions
    - Monte Carlo risk simulation
    - Cross-contract corpus intelligence
    """
    logger.info(f"Starting V11 analysis for '{request.contract_name}'")

    try:
        # Lazy import to avoid heavy load at startup
        from src.v10.pipeline import V10Pipeline

        pipeline = V10Pipeline(multilingual=True)

        report = pipeline.analyze(
            contract_text=request.contract_text,
            contract_type=request.contract_type,
            suggest_rewrites=request.suggest_rewrites,
            simulate_risk=request.simulate_risk,
            corpus_compare=request.corpus_compare,
            use_semantic_chunking=request.use_semantic_chunking,
        )

        return V11AnalyzeResponse(
            engine_version=report.engine_version,
            contract_type=report.contract_type,
            total_clauses=report.total_clauses,
            analysis_time_ms=report.analysis_time_ms,
            overall_risk_score=report.overall_risk_score,
            risk_level=report.risk_level,
            executive_summary=report.executive_summary,
            classifications=report.clause_classifications,
            graph_analysis=report.graph,
            power_analysis=report.power,
            dispute_prediction=report.disputes,
            suggested_rewrites=report.suggested_rewrites,
            risk_simulation=report.risk_simulation,
            corpus_comparison=report.corpus_comparison,
        )

    except Exception as e:
        logger.error(f"V11 analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== V12 QUAD-INNOVATION ENDPOINT ====================

class V12AnalyzeRequest(BaseModel):
    """V12 analysis request with quad-innovation toggles."""
    contract_text: str
    contract_name: str = "Untitled"
    contract_type: str = "MSA"
    # V11 base options
    suggest_rewrites: bool = True
    simulate_risk: bool = True
    corpus_compare: bool = True
    use_semantic_chunking: bool = True
    # V12 innovation toggles
    enable_symbolic: bool = True
    enable_rag: bool = True
    enable_gnn: bool = True
    enable_debate: bool = True


class V12AnalyzeResponse(BaseModel):
    """V12 analysis response with all four innovation outputs."""
    engine_version: str
    contract_type: str
    total_clauses: int
    analysis_time_ms: int
    v11_risk_score: float
    v12_fused_risk: float
    v12_confidence: float
    # V11 base
    classifications: List[Dict[str, Any]]
    graph_analysis: Dict[str, Any]
    power_analysis: Dict[str, Any]
    # V12 innovations
    symbolic_verdict: Optional[Dict[str, Any]] = None
    case_law_results: Optional[Dict[str, Any]] = None
    gnn_scores: Optional[Dict[str, Any]] = None
    debate_transcript: Optional[Dict[str, Any]] = None
    innovation_summary: Dict[str, str] = {}


@router.post("/v12-analyze", response_model=V12AnalyzeResponse)
async def analyze_contract_v12(request: V12AnalyzeRequest):
    """
    Run V12 quad-innovation pipeline:
    1. Neuro-Symbolic Legal Reasoning
    2. RAG Case Law Intelligence
    3. Graph Attention Network
    4. Multi-Agent Legal Debate
    """
    logger.info(f"Starting V12 analysis for '{request.contract_name}'")

    try:
        from src.v10.pipeline import V10Pipeline
        from src.v12.v12_engine import V12Engine

        # Phase 1: Run V11 pipeline
        pipeline = V10Pipeline(multilingual=True)
        v11_report = pipeline.analyze(
            contract_text=request.contract_text,
            contract_type=request.contract_type,
            suggest_rewrites=request.suggest_rewrites,
            simulate_risk=request.simulate_risk,
            corpus_compare=request.corpus_compare,
            use_semantic_chunking=request.use_semantic_chunking,
        )

        # Phase 2: Run V12 quad-innovation engine
        v12_engine = V12Engine()
        v12_report = v12_engine.analyze(
            v11_report,
            enable_symbolic=request.enable_symbolic,
            enable_rag=request.enable_rag,
            enable_gnn=request.enable_gnn,
            enable_debate=request.enable_debate,
        )

        return V12AnalyzeResponse(
            engine_version=v12_report.engine_version,
            contract_type=v12_report.v11_contract_type,
            total_clauses=v12_report.v11_clause_count,
            analysis_time_ms=v12_report.analysis_time_ms,
            v11_risk_score=v12_report.v11_risk_score,
            v12_fused_risk=v12_report.v12_fused_risk,
            v12_confidence=v12_report.v12_confidence,
            classifications=v11_report.clause_classifications,
            graph_analysis=v11_report.graph,
            power_analysis=v11_report.power,
            symbolic_verdict=(
                v12_report.symbolic_verdict.to_dict()
                if v12_report.symbolic_verdict else None
            ),
            case_law_results=(
                v12_report.case_law_results.to_dict()
                if v12_report.case_law_results else None
            ),
            gnn_scores=(
                v12_report.gnn_scores.to_dict()
                if v12_report.gnn_scores else None
            ),
            debate_transcript=(
                v12_report.debate_transcript.to_dict()
                if v12_report.debate_transcript else None
            ),
            innovation_summary=v12_report.innovation_summary,
        )

    except Exception as e:
        logger.error(f"V12 analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
