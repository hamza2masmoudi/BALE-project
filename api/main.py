"""
BALE API - Main FastAPI Application
Production-ready REST API for legal contract analysis.
"""
import os
import uuid
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from api.schemas import (
    AnalyzeClauseRequest, AnalysisResponse, ExplainableVerdictResponse,
    HarmonizationResponse, DecisionFactorResponse,
    SimulateTrialRequest, TrialSimulationResponse, TrialTranscriptEntry,
    ContractCreateRequest, ContractUpdateRequest, ContractResponse, ContractListResponse,
    HealthResponse, ErrorResponse,
    Jurisdiction, AnalysisDepth, InferenceMode
)
from src.graph import compile_graph
from src.explainability import ExplainabilityEngine, build_explainable_verdict
from src.logger import setup_logger

logger = setup_logger("bale_api")

# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, cleanup on shutdown."""
    logger.info("🚀 BALE API Starting...")
    
    # Pre-compile the graph for faster first request
    app.state.graph = compile_graph()
    app.state.explainability = ExplainabilityEngine()
    
    # Check inference availability
    app.state.local_available = bool(os.getenv("LOCAL_LLM_ENDPOINT"))
    app.state.mistral_available = bool(os.getenv("MISTRAL_API_KEY"))
    
    logger.info(f"Local LLM: {'✅' if app.state.local_available else '❌'}")
    logger.info(f"Mistral API: {'✅' if app.state.mistral_available else '❌'}")
    
    # Initialize cache
    try:
        from api.cache import init_cache
        if init_cache():
            logger.info("Redis cache: ✅")
        else:
            logger.info("Redis cache: ❌ (running without cache)")
    except Exception as e:
        logger.warning(f"Cache init failed: {e}")
    
    # Register extended routes
    try:
        from api.routes import register_routes
        register_routes(app)
    except Exception as e:
        logger.warning(f"Extended routes not loaded: {e}")
    
    # Register frontier routes
    try:
        from api.frontier_routes import router as frontier_router
        app.include_router(frontier_router, prefix="/api")
        logger.info("Frontier routes: ✅")
    except Exception as e:
        logger.warning(f"Frontier routes not loaded: {e}")
    
    # Register NLQ and generation routes
    try:
        from api.nlq_routes import router as nlq_router
        app.include_router(nlq_router, prefix="/api")
        logger.info("NLQ & Generation routes: ✅")
    except Exception as e:
        logger.warning(f"NLQ routes not loaded: {e}")
    
    yield
    
    logger.info("👋 BALE API Shutting down...")


# ==================== APP SETUP ====================

app = FastAPI(
    title="BALE API",
    description="""
## Binary Adjudication & Litigation Engine

BALE is a neuro-symbolic legal reasoning engine for contract risk analysis.

### Key Features
- **Multi-Agent Dialectic**: Civilist vs Commonist interpretation
- **Deterministic Adjudication**: Explainable, rule-based verdicts
- **Mock Trial Simulation**: Adversarial Plaintiff vs Defense
- **Harmonization**: AI-suggested clause improvements

### Authentication
API keys are required for production use. Include in header:
```
Authorization: Bearer YOUR_API_KEY
```
    """,
    version="2.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": f"HTTP_{exc.status_code}"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": "INTERNAL_ERROR"}
    )


# ==================== HEALTH ENDPOINTS ====================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check API health and component availability."""
    return HealthResponse(
        status="healthy",
        version="2.2.0",
        inference_local_available=app.state.local_available,
        inference_mistral_available=app.state.mistral_available,
        database_connected=True,  # TODO: Real DB check
        vector_store_ready=True   # TODO: Real check
    )


@app.get("/", tags=["System"])
async def root():
    """API root - redirect to docs."""
    return {
        "name": "BALE API",
        "version": "2.2.0",
        "docs": "/docs",
        "health": "/health"
    }


# ==================== ANALYSIS ENDPOINTS ====================

@app.post("/v1/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_clause(request: AnalyzeClauseRequest):
    """
    Analyze a contract clause for litigation risk.
    
    This endpoint runs the full BALE pipeline:
    1. Civilist interpretation (Civil Law)
    2. Commonist interpretation (Common Law)
    3. IP Specialist (if relevant)
    4. Synthesizer (measures interpretive gap)
    5. Mock Trial Simulation (Plaintiff vs Defense)
    6. Harmonizer (suggests improvements)
    
    Returns an explainable verdict with full decision trace.
    """
    start_time = time.time()
    analysis_id = str(uuid.uuid4())
    
    # Determine inference mode
    if request.inference_mode == InferenceMode.AUTO:
        mode = "mistral" if app.state.mistral_available else "local"
    else:
        mode = request.inference_mode.value
    
    # Validate mode availability
    if mode == "mistral" and not app.state.mistral_available:
        raise HTTPException(400, "Mistral API not configured. Set MISTRAL_API_KEY.")
    if mode == "local" and not app.state.local_available:
        raise HTTPException(400, "Local LLM not available. Check LOCAL_LLM_ENDPOINT.")
    
    try:
        # Run BALE graph
        initial_state = {
            "content": request.clause_text,
            "execution_mode": mode
        }
        
        result = app.state.graph.invoke(initial_state)
        report = result.get("final_report", {})
        
        # Build explainable verdict
        verdict = build_explainable_verdict(
            report=report,
            explainability_engine=app.state.explainability
        )
        
        # Build harmonization response if requested
        harmonization = None
        if request.include_harmonization and report.get("golden_clause"):
            golden = report.get("golden_clause", "")
            rationale = report.get("rationale", "")
            
            harmonization = HarmonizationResponse(
                golden_clause=golden if isinstance(golden, str) else str(golden),
                rationale=rationale if isinstance(rationale, str) else str(rationale),
                risk_reduction=max(0, verdict.risk_score - 35)  # Estimate
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return AnalysisResponse(
            id=analysis_id,
            verdict=verdict,
            harmonization=harmonization,
            raw_outputs=report if os.getenv("BALE_DEBUG") else None,
            processing_time_ms=processing_time,
            inference_mode_used=InferenceMode(mode)
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.post("/v1/simulate", response_model=TrialSimulationResponse, tags=["Simulation"])
async def simulate_trial(request: SimulateTrialRequest):
    """
    Run a full mock trial simulation.
    
    Simulates an adversarial legal proceeding:
    1. Plaintiff presents maximalist interpretation
    2. Defense presents minimalist rebuttal
    3. Judge extracts Boolean factors
    4. Symbolic adjudication calculates verdict
    
    Returns full transcript and decision factors.
    """
    simulation_id = str(uuid.uuid4())
    
    # Determine mode
    if request.inference_mode == InferenceMode.AUTO:
        mode = "mistral" if app.state.mistral_available else "local"
    else:
        mode = request.inference_mode.value
    
    try:
        # Run graph (we only need simulation node, but run full for context)
        initial_state = {
            "content": request.clause_text,
            "execution_mode": mode
        }
        
        result = app.state.graph.invoke(initial_state)
        report = result.get("final_report", {})
        
        # Parse transcript
        raw_transcript = report.get("transcript", "")
        transcript_entries = []
        
        if raw_transcript:
            lines = raw_transcript.split("\n\n")
            for line in lines:
                if "**Plaintiff**" in line:
                    transcript_entries.append(TrialTranscriptEntry(
                        speaker="PLAINTIFF",
                        content=line.replace("👨‍⚖️ **Plaintiff**:", "").strip()
                    ))
                elif "**Defense**" in line:
                    transcript_entries.append(TrialTranscriptEntry(
                        speaker="DEFENSE",
                        content=line.replace("🛡️ **Defense**:", "").strip()
                    ))
                elif "**Judicial" in line or "**Calculated" in line or "**Litigation" in line:
                    transcript_entries.append(TrialTranscriptEntry(
                        speaker="JUDGE",
                        content=line
                    ))
        
        risk = report.get("risk", 50)
        outcome = "PLAINTIFF_WIN" if risk > 50 else "DEFENSE_WIN" if risk < 50 else "SETTLEMENT"
        
        return TrialSimulationResponse(
            id=simulation_id,
            final_risk=risk,
            outcome=outcome,
            transcript=transcript_entries,
            judicial_factors={},  # TODO: Parse from report
            reasoning=report.get("logic", "N/A")
        )
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        raise HTTPException(500, f"Simulation failed: {str(e)}")


# ==================== CONTRACT CRUD (Placeholder) ====================
# These will be fully implemented when PostgreSQL is connected

@app.post("/v1/contracts", response_model=ContractResponse, tags=["Contracts"])
async def create_contract(request: ContractCreateRequest):
    """Store a contract for tracking and repeated analysis."""
    # TODO: Implement with PostgreSQL
    from datetime import datetime
    return ContractResponse(
        id=str(uuid.uuid4()),
        name=request.name,
        jurisdiction=request.jurisdiction,
        metadata=request.metadata or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        analysis_count=0,
        last_risk_score=None
    )


@app.get("/v1/contracts", response_model=ContractListResponse, tags=["Contracts"])
async def list_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    jurisdiction: Optional[Jurisdiction] = None
):
    """List all stored contracts with pagination."""
    # TODO: Implement with PostgreSQL
    return ContractListResponse(
        items=[],
        total=0,
        page=page,
        page_size=page_size
    )


@app.get("/v1/contracts/{contract_id}", response_model=ContractResponse, tags=["Contracts"])
async def get_contract(contract_id: str):
    """Get a specific contract by ID."""
    # TODO: Implement with PostgreSQL
    raise HTTPException(404, "Contract not found")


@app.patch("/v1/contracts/{contract_id}", response_model=ContractResponse, tags=["Contracts"])
async def update_contract(contract_id: str, request: ContractUpdateRequest):
    """Update contract metadata."""
    # TODO: Implement with PostgreSQL
    raise HTTPException(404, "Contract not found")


@app.delete("/v1/contracts/{contract_id}", tags=["Contracts"])
async def delete_contract(contract_id: str):
    """Delete a contract."""
    # TODO: Implement with PostgreSQL
    raise HTTPException(404, "Contract not found")


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8080)),
        reload=os.getenv("BALE_ENV") == "development"
    )
