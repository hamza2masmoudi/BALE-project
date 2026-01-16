"""
BALE NLQ and Generation API Routes
Natural language queries and contract generation endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.nlq import nlq_engine, QueryResult
from src.generation import contract_generator, GenerationRequest, ContractStyle
from src.logger import setup_logger

logger = setup_logger("nlq_api")

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])


# ==================== REQUEST/RESPONSE MODELS ====================

class NLQueryRequest(BaseModel):
    """Natural language query request."""
    query: str = Field(..., description="Natural language query")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Conversation context")


class NLQueryResponse(BaseModel):
    """Natural language query response."""
    query: str
    intent: str
    answer: str
    confidence: float
    data: Dict[str, Any]
    sources: List[str]
    follow_up_suggestions: List[str]


class ContractGenerateRequest(BaseModel):
    """Contract generation request."""
    # Simple mode - just a prompt
    prompt: Optional[str] = Field(default=None, description="Natural language description")
    
    # Detailed mode
    contract_type: Optional[str] = Field(default="msa", description="Contract type")
    description: Optional[str] = Field(default=None, description="Contract description")
    jurisdiction: str = Field(default="US", description="Legal jurisdiction")
    industry: str = Field(default="technology", description="Industry sector")
    
    party_a_name: str = Field(default="Party A", description="First party name")
    party_a_type: str = Field(default="corporation", description="First party type")
    party_b_name: str = Field(default="Party B", description="Second party name")
    party_b_type: str = Field(default="corporation", description="Second party type")
    
    your_position: str = Field(default="neutral", description="Your position: buyer, seller, neutral")
    style: str = Field(default="balanced", description="Contract style")
    
    term_months: int = Field(default=12, description="Contract term in months")
    auto_renew: bool = Field(default=True, description="Auto-renewal")
    
    include_clauses: List[str] = Field(default=[], description="Clauses to include")
    exclude_clauses: List[str] = Field(default=[], description="Clauses to exclude")
    special_requirements: str = Field(default="", description="Special requirements")


class ContractGenerateResponse(BaseModel):
    """Contract generation response."""
    contract_id: str
    contract_type: str
    title: str
    full_text: str
    sections: List[Dict[str, str]]
    metadata: Dict[str, Any]
    risk_score: int
    warnings: List[str]
    generated_at: str


class ChatMessage(BaseModel):
    """Chat message in conversation."""
    role: str  # user, assistant
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    data: Optional[Dict[str, Any]] = None


class ConversationRequest(BaseModel):
    """Multi-turn conversation request."""
    messages: List[ChatMessage]
    context: Optional[Dict[str, Any]] = None


# ==================== NLQ ENDPOINTS ====================

@router.post("/query", response_model=NLQueryResponse)
async def query(request: NLQueryRequest):
    """
    Process a natural language query about contracts.
    
    Examples:
    - "What is my total risk exposure?"
    - "Find all NDAs with UK jurisdiction"
    - "Show me contracts expiring in the next 90 days"
    - "Explain the indemnification clause"
    """
    try:
        result = nlq_engine.query(request.query, request.context)
        return NLQueryResponse(
            query=result.query,
            intent=result.intent.value,
            answer=result.answer,
            confidence=result.confidence,
            data=result.data,
            sources=result.sources,
            follow_up_suggestions=result.follow_up_suggestions
        )
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(request: ConversationRequest):
    """
    Multi-turn conversation interface.
    Maintains context across messages.
    """
    try:
        # Get the latest user message
        user_messages = [m for m in request.messages if m.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        latest_query = user_messages[-1].content
        
        # Build context from conversation history
        context = request.context or {}
        context["history"] = [{"role": m.role, "content": m.content} for m in request.messages[-10:]]
        
        # Process query
        result = nlq_engine.query(latest_query, context)
        
        # Return response
        return {
            "response": ChatMessage(
                role="assistant",
                content=result.answer,
                data=result.data
            ),
            "intent": result.intent.value,
            "confidence": result.confidence,
            "suggestions": result.follow_up_suggestions
        }
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GENERATION ENDPOINTS ====================

@router.post("/generate", response_model=ContractGenerateResponse)
async def generate_contract(request: ContractGenerateRequest):
    """
    Generate a complete contract from requirements.
    
    Can use either:
    - Simple mode: Just provide a 'prompt' describing what you need
    - Detailed mode: Specify all parameters
    """
    try:
        if request.prompt:
            # Simple mode - generate from prompt
            generated = contract_generator.generate_from_prompt(request.prompt)
        else:
            # Detailed mode
            style_map = {
                "formal": ContractStyle.FORMAL,
                "plain_english": ContractStyle.PLAIN_ENGLISH,
                "balanced": ContractStyle.BALANCED,
                "aggressive": ContractStyle.AGGRESSIVE,
                "protective": ContractStyle.PROTECTIVE,
            }
            
            gen_request = GenerationRequest(
                contract_type=request.contract_type or "msa",
                description=request.description or "General services",
                jurisdiction=request.jurisdiction,
                industry=request.industry,
                party_a_name=request.party_a_name,
                party_a_type=request.party_a_type,
                party_b_name=request.party_b_name,
                party_b_type=request.party_b_type,
                your_position=request.your_position,
                style=style_map.get(request.style, ContractStyle.BALANCED),
                term_months=request.term_months,
                auto_renew=request.auto_renew,
                include_clauses=request.include_clauses,
                exclude_clauses=request.exclude_clauses,
                special_requirements=request.special_requirements,
            )
            generated = contract_generator.generate(gen_request)
        
        return ContractGenerateResponse(
            contract_id=generated.contract_id,
            contract_type=generated.contract_type,
            title=generated.title,
            full_text=generated.full_text,
            sections=generated.sections,
            metadata=generated.metadata,
            risk_score=generated.risk_score,
            warnings=generated.warnings,
            generated_at=generated.generated_at
        )
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates():
    """List available contract templates and clause types."""
    return {
        "contract_types": [
            {"id": "msa", "name": "Master Services Agreement", "description": "Comprehensive services agreement"},
            {"id": "nda", "name": "Non-Disclosure Agreement", "description": "Confidentiality protection"},
            {"id": "sla", "name": "Service Level Agreement", "description": "Uptime and support commitments"},
            {"id": "license", "name": "Software License", "description": "Software usage rights"},
            {"id": "employment", "name": "Employment Agreement", "description": "Employment terms"},
            {"id": "consulting", "name": "Consulting Agreement", "description": "Consulting engagement"},
            {"id": "vendor", "name": "Vendor Agreement", "description": "Supplier relationship"},
            {"id": "partnership", "name": "Partnership Agreement", "description": "Business partnership"},
        ],
        "jurisdictions": [
            {"id": "US", "name": "United States"},
            {"id": "UK", "name": "United Kingdom"},
            {"id": "EU", "name": "European Union"},
            {"id": "GERMANY", "name": "Germany"},
            {"id": "SINGAPORE", "name": "Singapore"},
        ],
        "styles": [
            {"id": "formal", "name": "Formal", "description": "Traditional legal language"},
            {"id": "plain_english", "name": "Plain English", "description": "Simplified language"},
            {"id": "balanced", "name": "Balanced", "description": "Fair to both parties"},
            {"id": "protective", "name": "Protective", "description": "Favors your position"},
            {"id": "aggressive", "name": "Aggressive", "description": "Strongly favors your position"},
        ],
        "clause_sections": [
            "recitals", "definitions", "services", "fees", "term_termination",
            "ip", "confidentiality", "warranties", "indemnification",
            "limitation_of_liability", "force_majeure", "dispute_resolution", "general"
        ]
    }


@router.post("/suggest")
async def suggest_clauses(request: ContractGenerateRequest):
    """Get AI suggestions for contract clauses based on requirements."""
    suggestions = []
    
    # Based on contract type and position, suggest clauses
    if request.your_position == "buyer":
        suggestions.append({
            "section": "ip",
            "suggestion": "Consider requesting work-for-hire ownership of deliverables",
            "priority": "high"
        })
        suggestions.append({
            "section": "liability",
            "suggestion": "Ensure adequate liability cap (12-24 months of fees typical)",
            "priority": "high"
        })
    elif request.your_position == "seller":
        suggestions.append({
            "section": "ip",
            "suggestion": "Retain ownership of pre-existing IP and tools",
            "priority": "high"
        })
        suggestions.append({
            "section": "liability",
            "suggestion": "Include reasonable liability cap with appropriate carveouts",
            "priority": "high"
        })
    
    if request.jurisdiction in ["EU", "GERMANY"]:
        suggestions.append({
            "section": "data_protection",
            "suggestion": "Include GDPR-compliant data processing addendum",
            "priority": "critical"
        })
    
    return {"suggestions": suggestions}


# ==================== QUICK ACTIONS ====================

@router.get("/quick-queries")
async def quick_queries():
    """Get list of common quick queries."""
    return {
        "queries": [
            {"id": "risk", "label": "Risk Summary", "query": "What is my total risk exposure?"},
            {"id": "high_risk", "label": "High Risk", "query": "Show me high-risk contracts"},
            {"id": "expiring", "label": "Expiring Soon", "query": "What contracts expire in next 90 days?"},
            {"id": "stats", "label": "Portfolio Stats", "query": "Give me a portfolio summary"},
            {"id": "entities", "label": "Top Counterparties", "query": "Who are my biggest counterparties?"},
            {"id": "compare", "label": "Market Comparison", "query": "How do my terms compare to market?"},
        ]
    }
