"""
BALE V8 Explainable AI Module
Full audit trails with legal citations for every decision.
"""
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

from src.logger import setup_logger

logger = setup_logger("bale_explainability_v8")


class CitationApplication(str, Enum):
    """How a citation was applied in analysis."""
    SUPPORTS = "SUPPORTS"           # Citation supports the conclusion
    DISTINGUISHES = "DISTINGUISHES" # Citation was distinguished (different facts)
    OVERRULED = "OVERRULED"         # Citation is no longer good law
    APPLIES = "APPLIES"             # Citation directly applies
    INTERPRETS = "INTERPRETS"       # Citation provides interpretation


class Jurisdiction(str, Enum):
    """Supported jurisdictions."""
    UK = "UK"
    FR = "FR"
    EU = "EU"
    INTERNATIONAL = "INTERNATIONAL"


@dataclass
class LegalCitation:
    """A legal citation used in analysis."""
    source: str                         # "Art. 1231-3 CC" or "Photo Production v Securicor [1980]"
    authority_level: int                # 0-100 (higher = more authoritative)
    jurisdiction: Jurisdiction
    relevance_score: float              # 0.0-1.0
    quote: Optional[str] = None         # Relevant passage
    how_applied: CitationApplication = CitationApplication.APPLIES
    url: Optional[str] = None           # Link to source if available
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "authority_level": self.authority_level,
            "jurisdiction": self.jurisdiction.value,
            "relevance_score": self.relevance_score,
            "quote": self.quote,
            "how_applied": self.how_applied.value,
            "url": self.url
        }


@dataclass
class RiskFactor:
    """Individual factor contributing to risk score."""
    name: str                           # "ambiguity_detected"
    description: str                    # "Clause contains ambiguous language"
    contribution: float                 # Points added/subtracted (e.g., +20, -10)
    confidence: float                   # 0.0-1.0
    supporting_citations: List[LegalCitation] = field(default_factory=list)
    evidence: Optional[str] = None      # Text evidence from clause
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "contribution": self.contribution,
            "confidence": self.confidence,
            "citations": [c.to_dict() for c in self.supporting_citations],
            "evidence": self.evidence
        }


@dataclass
class ReasoningStep:
    """A step in the reasoning chain."""
    step_number: int
    action: str                         # What was done
    result: str                         # What was found
    agent: Optional[str] = None         # Which agent performed this
    duration_ms: Optional[int] = None   # How long it took
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass 
class ExplainableVerdict:
    """Complete explainable verdict with full audit trail."""
    
    # Core verdict
    clause_id: str
    clause_text: str
    risk_score: float                   # 0-100
    risk_level: str                     # LOW, MEDIUM, HIGH, CRITICAL
    clause_type: str                    # Classification result
    
    # Reasoning chain
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    
    # Factor breakdown
    risk_factors: List[RiskFactor] = field(default_factory=list)
    
    # All citations used
    citations: List[LegalCitation] = field(default_factory=list)
    
    # Problems and recommendations
    problems_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Counter-arguments considered
    rejected_arguments: List[str] = field(default_factory=list)
    
    # Confidence
    confidence_score: float = 0.85      # Overall confidence
    confidence_lower: float = 0.0       # Lower bound
    confidence_upper: float = 0.0       # Upper bound
    
    # Specialist analyses
    specialist_analyses: Dict[str, str] = field(default_factory=dict)
    
    # Audit metadata
    analysis_timestamp: str = ""
    model_version: str = "V8"
    decision_hash: str = ""             # SHA256 for reproducibility
    
    def __post_init__(self):
        if not self.analysis_timestamp:
            self.analysis_timestamp = datetime.utcnow().isoformat()
        if not self.decision_hash:
            self.decision_hash = self._compute_hash()
        if self.confidence_lower == 0 and self.confidence_upper == 0:
            margin = (1 - self.confidence_score) * 20
            self.confidence_lower = max(0, self.risk_score - margin)
            self.confidence_upper = min(100, self.risk_score + margin)
    
    def _compute_hash(self) -> str:
        """Compute reproducibility hash."""
        content = f"{self.clause_text}:{self.risk_score}:{self.clause_type}:{self.model_version}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_risk_breakdown(self) -> str:
        """Get human-readable risk breakdown."""
        lines = [
            f"═══════════════════════════════════════════",
            f"           RISK BREAKDOWN                   ",
            f"═══════════════════════════════════════════",
            f"",
            f"Base Risk:                    50%",
        ]
        
        total_contribution = 0
        for factor in self.risk_factors:
            sign = "+" if factor.contribution > 0 else ""
            bar_len = int(abs(factor.contribution) / 2)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            lines.append(f"{factor.name:25} {bar} {sign}{factor.contribution:>5.0f}%")
            total_contribution += factor.contribution
        
        lines.extend([
            f"───────────────────────────────────────────",
            f"TOTAL RISK:                   {self.risk_score:.0f}%",
            f"",
            f"Confidence: {self.confidence_score*100:.0f}% [{self.confidence_lower:.0f}% - {self.confidence_upper:.0f}%]",
            f"",
            f"KEY CITATIONS:"
        ])
        
        for citation in self.citations[:5]:
            lines.append(f"• {citation.source} - {citation.how_applied.value}")
        
        lines.append(f"═══════════════════════════════════════════")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "clause_id": self.clause_id,
            "clause_text": self.clause_text[:500] + "..." if len(self.clause_text) > 500 else self.clause_text,
            "verdict": {
                "risk_score": self.risk_score,
                "risk_level": self.risk_level,
                "clause_type": self.clause_type,
                "confidence": {
                    "score": self.confidence_score,
                    "lower_bound": self.confidence_lower,
                    "upper_bound": self.confidence_upper
                }
            },
            "reasoning": {
                "steps": [s.to_dict() for s in self.reasoning_steps],
                "factors": [f.to_dict() for f in self.risk_factors],
                "citations": [c.to_dict() for c in self.citations],
                "rejected_arguments": self.rejected_arguments
            },
            "recommendations": {
                "problems": self.problems_detected,
                "suggestions": self.recommendations
            },
            "specialist_analyses": self.specialist_analyses,
            "audit": {
                "timestamp": self.analysis_timestamp,
                "model_version": self.model_version,
                "decision_hash": self.decision_hash
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ==================== CITATION DATABASE ====================

# Key legal references for FR/UK
LEGAL_CITATIONS = {
    # French Civil Code
    "ambiguity_fr": LegalCitation(
        source="Art. 1188 CC (ancien 1156)",
        authority_level=90,
        jurisdiction=Jurisdiction.FR,
        relevance_score=0.9,
        quote="On doit dans les conventions rechercher quelle a été la commune intention des parties contractantes",
        how_applied=CitationApplication.APPLIES
    ),
    "good_faith_fr": LegalCitation(
        source="Art. 1104 CC",
        authority_level=90,
        jurisdiction=Jurisdiction.FR,
        relevance_score=0.95,
        quote="Les contrats doivent être négociés, formés et exécutés de bonne foi",
        how_applied=CitationApplication.APPLIES
    ),
    "force_majeure_fr": LegalCitation(
        source="Art. 1218 CC",
        authority_level=90,
        jurisdiction=Jurisdiction.FR,
        relevance_score=0.9,
        quote="Il y a force majeure en matière contractuelle lorsqu'un événement échappant au contrôle du débiteur...",
        how_applied=CitationApplication.APPLIES
    ),
    "limitation_fr": LegalCitation(
        source="Art. 1231-3 CC",
        authority_level=90,
        jurisdiction=Jurisdiction.FR,
        relevance_score=0.85,
        quote="Le débiteur n'est tenu que des dommages et intérêts qui étaient prévus ou prévisibles",
        how_applied=CitationApplication.APPLIES
    ),
    "non_compete_fr": LegalCitation(
        source="Cass. Soc., 10 juillet 2002",
        authority_level=85,
        jurisdiction=Jurisdiction.FR,
        relevance_score=0.9,
        quote="La clause de non-concurrence n'est licite que si elle comporte une contrepartie financière",
        how_applied=CitationApplication.APPLIES
    ),
    
    # UK Common Law
    "contra_proferentem_uk": LegalCitation(
        source="Canada Steamship Lines v The King [1952]",
        authority_level=85,
        jurisdiction=Jurisdiction.UK,
        relevance_score=0.9,
        quote="If a clause is ambiguous, it will be construed against the party seeking to rely on it",
        how_applied=CitationApplication.APPLIES
    ),
    "exclusion_uk": LegalCitation(
        source="Photo Production v Securicor [1980]",
        authority_level=85,
        jurisdiction=Jurisdiction.UK,
        relevance_score=0.85,
        quote="Courts should give effect to exclusion clauses in commercial contracts between parties of equal bargaining power",
        how_applied=CitationApplication.APPLIES
    ),
    "ucta_uk": LegalCitation(
        source="UCTA 1977 s.2-3",
        authority_level=95,
        jurisdiction=Jurisdiction.UK,
        relevance_score=0.9,
        quote="Cannot exclude liability for death or personal injury caused by negligence",
        how_applied=CitationApplication.APPLIES
    ),
    "restraint_uk": LegalCitation(
        source="Nordenfelt v Maxim Nordenfelt [1894]",
        authority_level=85,
        jurisdiction=Jurisdiction.UK,
        relevance_score=0.85,
        quote="Restraints of trade are prima facie void unless shown to be reasonable",
        how_applied=CitationApplication.APPLIES
    ),
    "mac_uk": LegalCitation(
        source="Grupo Hotelero Urvasco v Carey Value Added [2013]",
        authority_level=80,
        jurisdiction=Jurisdiction.UK,
        relevance_score=0.8,
        quote="MAC clauses require a high threshold of materiality",
        how_applied=CitationApplication.APPLIES
    ),
    
    # GDPR
    "gdpr_28": LegalCitation(
        source="GDPR Art. 28",
        authority_level=95,
        jurisdiction=Jurisdiction.EU,
        relevance_score=0.95,
        quote="Processing by a processor shall be governed by a contract that sets out the subject-matter and duration...",
        how_applied=CitationApplication.APPLIES
    ),
    "schrems_ii": LegalCitation(
        source="Schrems II (C-311/18)",
        authority_level=95,
        jurisdiction=Jurisdiction.EU,
        relevance_score=0.9,
        quote="SCCs alone may not be sufficient; supplementary measures may be required",
        how_applied=CitationApplication.APPLIES
    ),
}


def get_relevant_citations(clause_type: str, jurisdiction: str = "both") -> List[LegalCitation]:
    """Get relevant citations for a clause type."""
    citations = []
    
    # Map clause types to citations
    citation_map = {
        "ambiguity": ["ambiguity_fr", "contra_proferentem_uk"],
        "indemnification": ["limitation_fr", "ucta_uk"],
        "limitation_liability": ["limitation_fr", "exclusion_uk", "ucta_uk"],
        "exclusion": ["exclusion_uk", "ucta_uk", "limitation_fr"],
        "force_majeure": ["force_majeure_fr"],
        "non_compete": ["non_compete_fr", "restraint_uk"],
        "gdpr": ["gdpr_28", "schrems_ii"],
        "mac": ["mac_uk"],
        "good_faith": ["good_faith_fr"],
    }
    
    for key, citation_keys in citation_map.items():
        if key in clause_type.lower():
            for ck in citation_keys:
                if ck in LEGAL_CITATIONS:
                    citation = LEGAL_CITATIONS[ck]
                    if jurisdiction == "both" or citation.jurisdiction.value == jurisdiction:
                        citations.append(citation)
    
    return citations


# ==================== VERDICT BUILDER ====================

class ExplainableVerdictBuilder:
    """Builder for creating explainable verdicts."""
    
    def __init__(self, clause_id: str, clause_text: str):
        self.clause_id = clause_id
        self.clause_text = clause_text
        self.risk_factors: List[RiskFactor] = []
        self.reasoning_steps: List[ReasoningStep] = []
        self.citations: List[LegalCitation] = []
        self.problems: List[str] = []
        self.recommendations: List[str] = []
        self.rejected_arguments: List[str] = []
        self.specialist_analyses: Dict[str, str] = {}
        self.clause_type = ""
        self.step_counter = 0
    
    def add_reasoning_step(self, action: str, result: str, agent: str = None, duration_ms: int = None):
        """Add a step to the reasoning chain."""
        self.step_counter += 1
        self.reasoning_steps.append(ReasoningStep(
            step_number=self.step_counter,
            action=action,
            result=result,
            agent=agent,
            duration_ms=duration_ms
        ))
        return self
    
    def add_risk_factor(self, name: str, description: str, contribution: float, 
                       confidence: float = 0.9, evidence: str = None):
        """Add a risk factor."""
        factor = RiskFactor(
            name=name,
            description=description,
            contribution=contribution,
            confidence=confidence,
            evidence=evidence
        )
        self.risk_factors.append(factor)
        return self
    
    def add_citation(self, citation: LegalCitation):
        """Add a supporting citation."""
        self.citations.append(citation)
        return self
    
    def add_citations_for_type(self, clause_type: str):
        """Automatically add relevant citations for clause type."""
        relevant = get_relevant_citations(clause_type)
        self.citations.extend(relevant)
        return self
    
    def add_problem(self, problem: str):
        """Add a detected problem."""
        self.problems.append(problem)
        return self
    
    def add_recommendation(self, recommendation: str):
        """Add a recommendation."""
        self.recommendations.append(recommendation)
        return self
    
    def set_clause_type(self, clause_type: str):
        """Set the classified clause type."""
        self.clause_type = clause_type
        return self
    
    def add_specialist_analysis(self, specialist: str, analysis: str):
        """Add specialist agent analysis."""
        self.specialist_analyses[specialist] = analysis
        return self
    
    def build(self) -> ExplainableVerdict:
        """Build the final explainable verdict."""
        # Calculate risk score from factors
        base_risk = 50
        total_contribution = sum(f.contribution for f in self.risk_factors)
        risk_score = max(0, min(100, base_risk + total_contribution))
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Calculate confidence
        if self.risk_factors:
            avg_confidence = sum(f.confidence for f in self.risk_factors) / len(self.risk_factors)
        else:
            avg_confidence = 0.7
        
        return ExplainableVerdict(
            clause_id=self.clause_id,
            clause_text=self.clause_text,
            risk_score=risk_score,
            risk_level=risk_level,
            clause_type=self.clause_type,
            reasoning_steps=self.reasoning_steps,
            risk_factors=self.risk_factors,
            citations=self.citations,
            problems_detected=self.problems,
            recommendations=self.recommendations,
            rejected_arguments=self.rejected_arguments,
            specialist_analyses=self.specialist_analyses,
            confidence_score=avg_confidence
        )


# Export
__all__ = [
    "LegalCitation",
    "CitationApplication",
    "Jurisdiction", 
    "RiskFactor",
    "ReasoningStep",
    "ExplainableVerdict",
    "ExplainableVerdictBuilder",
    "LEGAL_CITATIONS",
    "get_relevant_citations"
]
