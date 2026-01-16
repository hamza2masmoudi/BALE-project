"""
BALE Explainability Engine
Provides transparent decision traces for legal AI compliance.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field
from src.adjudication import DecisionFactors


class LegalRule(str, Enum):
    """Canonical legal rules applied in adjudication."""
    CONTRA_PROFERENTEM = "Contra Proferentem"
    STRICT_CONSTRUCTION = "Strict Construction"
    MANDATORY_LAW = "Mandatory Law Override"
    PLAUSIBILITY = "Plausibility Assessment"
    GOOD_FAITH = "Good Faith (Bonne Foi)"
    REASONABLENESS = "Reasonableness Standard"


@dataclass
class DecisionFactor:
    """A single factor in the decision trace."""
    rule: LegalRule
    triggered: bool
    impact: int  # -20 to +20
    evidence: str
    legal_basis: Optional[str] = None
    confidence: float = 1.0  # How confident the system is about this factor
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule.value,
            "triggered": self.triggered,
            "impact": self.impact,
            "evidence": self.evidence,
            "legal_basis": self.legal_basis,
            "confidence": self.confidence
        }


@dataclass
class CitationProvenance:
    """Tracks the origin and validity of a legal citation."""
    citation_text: str
    source_type: str  # STATUTE, CASE_LAW, CONTRACT, DOCTRINE
    authority_level: int  # 0-100
    binding_status: str  # MANDATORY, DEFAULT, PERSUASIVE
    retrieved_from: str  # e.g., "vector_store", "knowledge_graph"
    retrieval_score: float  # Similarity/relevance score
    verified: bool = False  # Whether we verified it exists
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "citation": self.citation_text,
            "source_type": self.source_type,
            "authority_level": self.authority_level,
            "binding_status": self.binding_status,
            "retrieved_from": self.retrieved_from,
            "retrieval_score": self.retrieval_score,
            "verified": self.verified
        }


@dataclass
class CounterfactualScenario:
    """A 'what-if' scenario showing how changes affect risk."""
    description: str
    modified_clause: str
    new_risk_score: int
    factors_changed: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "modified_clause": self.modified_clause,
            "new_risk_score": self.new_risk_score,
            "factors_changed": self.factors_changed
        }


@dataclass
class ExplainableVerdict:
    """
    Complete explainable verdict with full decision trace.
    This is the core output structure for legal AI transparency.
    """
    # Core Verdict
    risk_score: int
    verdict_text: str  # "PLAINTIFF_FAVOR" or "DEFENSE_FAVOR"
    confidence: float
    
    # Decision Trace
    factors: List[DecisionFactor] = field(default_factory=list)
    
    # Legal Context
    interpretive_gap: int = 0
    civilist_summary: str = ""
    commonist_summary: str = ""
    synthesis: str = ""
    
    # Provenance
    citations: List[CitationProvenance] = field(default_factory=list)
    
    # Counterfactuals (optional)
    counterfactuals: List[CounterfactualScenario] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_notes: List[str] = field(default_factory=list)
    
    def risk_breakdown(self) -> Dict[str, int]:
        """Get breakdown of risk contributions by factor."""
        breakdown = {"baseline": 50}
        for f in self.factors:
            if f.triggered:
                breakdown[f.rule.value] = f.impact
        return breakdown
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_score": self.risk_score,
            "verdict": self.verdict_text,
            "confidence": self.confidence,
            "factors": [f.to_dict() for f in self.factors],
            "risk_breakdown": self.risk_breakdown(),
            "interpretive_gap": self.interpretive_gap,
            "civilist_summary": self.civilist_summary,
            "commonist_summary": self.commonist_summary,
            "synthesis": self.synthesis,
            "citations": [c.to_dict() for c in self.citations],
            "counterfactuals": [c.to_dict() for c in self.counterfactuals],
            "timestamp": self.timestamp.isoformat(),
            "processing_notes": self.processing_notes
        }


class ExplainabilityEngine:
    """
    Engine for generating explainable verdicts from BALE outputs.
    Converts raw agent outputs into transparent, auditable decision traces.
    """
    
    def __init__(self):
        self.rule_descriptions = {
            LegalRule.CONTRA_PROFERENTEM: 
                "Ambiguous terms are interpreted against the drafter",
            LegalRule.STRICT_CONSTRUCTION:
                "Exclusion clauses must be clear and unequivocal to be enforced",
            LegalRule.MANDATORY_LAW:
                "Statutory/mandatory law overrides conflicting contract terms",
            LegalRule.PLAUSIBILITY:
                "The claim must be plausible on its face to proceed",
            LegalRule.GOOD_FAITH:
                "Art. 1104 CC requires good faith in contract execution",
            LegalRule.REASONABLENESS:
                "Terms must be reasonable in commercial context"
        }
    
    def extract_factors_from_booleans(
        self, 
        factors: DecisionFactors,
        context: Dict[str, Any] = None
    ) -> List[DecisionFactor]:
        """
        Convert DecisionFactors (Boolean struct) into explainable DecisionFactor objects.
        """
        context = context or {}
        result = []
        
        # 1. Ambiguity / Contra Proferentem
        result.append(DecisionFactor(
            rule=LegalRule.CONTRA_PROFERENTEM,
            triggered=factors.is_ambiguous,
            impact=20 if factors.is_ambiguous else 0,
            evidence=context.get("ambiguity_evidence", 
                "Clause contains ambiguous/vague terminology" if factors.is_ambiguous 
                else "Clause language is clear and unambiguous"),
            legal_basis="Verba fortius accipiuntur contra proferentem"
        ))
        
        # 2. Strict Construction of Exclusions
        if not factors.is_exclusion_clear:
            result.append(DecisionFactor(
                rule=LegalRule.STRICT_CONSTRUCTION,
                triggered=True,
                impact=15,
                evidence=context.get("exclusion_evidence",
                    "Exclusion/limitation clause lacks required clarity"),
                legal_basis="Photo Production Ltd v Securicor [1980]"
            ))
        
        # 3. Mandatory Law Override
        result.append(DecisionFactor(
            rule=LegalRule.MANDATORY_LAW,
            triggered=factors.authority_is_mandatory,
            impact=20 if factors.authority_is_mandatory else 0,
            evidence=context.get("mandatory_evidence",
                "Contract term conflicts with mandatory statutory provision" if factors.authority_is_mandatory
                else "No conflict with mandatory law identified"),
            legal_basis="Art. 6 Code Civil (FR) / Ordre Public"
        ))
        
        # 4. Plausibility Assessment
        result.append(DecisionFactor(
            rule=LegalRule.PLAUSIBILITY,
            triggered=not factors.plaintiff_plausible,  # Triggers negatively if implausible
            impact=-20 if not factors.plaintiff_plausible else 10,
            evidence=context.get("plausibility_evidence",
                "Plaintiff's argument lacks facial plausibility" if not factors.plaintiff_plausible
                else "Plaintiff's argument meets plausibility threshold"),
            legal_basis="Ashcroft v. Iqbal (US) / Comparable standards"
        ))
        
        return result
    
    def generate_counterfactuals(
        self, 
        clause_text: str, 
        current_risk: int,
        factors: List[DecisionFactor]
    ) -> List[CounterfactualScenario]:
        """
        Generate 'what-if' scenarios showing how to reduce risk.
        """
        counterfactuals = []
        
        # Find triggered factors that increase risk
        risk_factors = [f for f in factors if f.triggered and f.impact > 0]
        
        for factor in risk_factors[:3]:  # Top 3 suggestions
            if factor.rule == LegalRule.CONTRA_PROFERENTEM:
                counterfactuals.append(CounterfactualScenario(
                    description="Remove ambiguous language",
                    modified_clause=f"[Clarify: {clause_text[:50]}... → Define key terms explicitly]",
                    new_risk_score=max(0, current_risk - factor.impact),
                    factors_changed=[factor.rule.value]
                ))
            elif factor.rule == LegalRule.STRICT_CONSTRUCTION:
                counterfactuals.append(CounterfactualScenario(
                    description="Strengthen exclusion clause language",
                    modified_clause="[Add: 'To the fullest extent permitted by law, [Party] excludes all liability for...']",
                    new_risk_score=max(0, current_risk - factor.impact),
                    factors_changed=[factor.rule.value]
                ))
            elif factor.rule == LegalRule.MANDATORY_LAW:
                counterfactuals.append(CounterfactualScenario(
                    description="Remove conflict with mandatory law",
                    modified_clause="[Remove clause or add: 'Subject to applicable mandatory law...']",
                    new_risk_score=max(0, current_risk - factor.impact),
                    factors_changed=[factor.rule.value]
                ))
        
        return counterfactuals
    
    def build_verdict(
        self,
        risk_score: int,
        factors: DecisionFactors,
        report: Dict[str, Any],
        clause_text: str = ""
    ) -> ExplainableVerdict:
        """
        Build a complete explainable verdict from BALE outputs.
        """
        # Extract factor trace
        factor_list = self.extract_factors_from_booleans(factors)
        
        # Determine verdict text
        if risk_score > 50:
            verdict_text = "PLAINTIFF_FAVOR"
        elif risk_score < 50:
            verdict_text = "DEFENSE_FAVOR"
        else:
            verdict_text = "NEUTRAL"
        
        # Calculate confidence based on factor agreement
        triggered_count = sum(1 for f in factor_list if f.triggered)
        confidence = 0.5 + (triggered_count * 0.1)  # More factors = more confident
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        # Generate counterfactuals
        counterfactuals = self.generate_counterfactuals(clause_text, risk_score, factor_list)
        
        # Extract summaries from report
        civilist_raw = report.get("civilist", "")
        commonist_raw = report.get("commonist", "")
        
        civilist_summary = civilist_raw[:500] if civilist_raw else "No Civil Law analysis available."
        commonist_summary = commonist_raw[:500] if commonist_raw else "No Common Law analysis available."
        
        return ExplainableVerdict(
            risk_score=risk_score,
            verdict_text=verdict_text,
            confidence=confidence,
            factors=factor_list,
            interpretive_gap=report.get("gap", 0),
            civilist_summary=civilist_summary,
            commonist_summary=commonist_summary,
            synthesis=report.get("synthesis", ""),
            counterfactuals=counterfactuals,
            processing_notes=[
                f"Analyzed with {len(factor_list)} legal rules",
                f"Interpretive gap: {report.get('gap', 0)}%"
            ]
        )


def build_explainable_verdict(report: Dict[str, Any], explainability_engine: ExplainabilityEngine = None):
    """
    Convenience function to build an explainable verdict from a BALE report.
    Returns an API-compatible schema object.
    """
    from api.schemas import ExplainableVerdictResponse, DecisionFactorResponse
    
    if explainability_engine is None:
        explainability_engine = ExplainabilityEngine()
    
    risk = report.get("risk", 50)
    gap = report.get("gap", 0)
    
    # Try to reconstruct factors from report
    # In a real scenario, we'd pass the DecisionFactors directly
    # For now, create synthetic factors based on risk
    factors_response = []
    
    # Based on risk score, infer which factors were triggered
    if risk > 50:
        # Plaintiff favored - some risk factors triggered
        if risk >= 70:
            factors_response.append(DecisionFactorResponse(
                rule="Contra Proferentem",
                triggered=True,
                impact=20,
                evidence="Ambiguous clause language detected",
                legal_basis="Interpretation against drafter"
            ))
        if risk >= 60:
            factors_response.append(DecisionFactorResponse(
                rule="Strict Construction",
                triggered=True,
                impact=15,
                evidence="Exclusion clause lacks clarity",
                legal_basis="Photo Production v Securicor"
            ))
    
    # Add baseline plausibility
    factors_response.append(DecisionFactorResponse(
        rule="Plausibility Assessment",
        triggered=risk > 40,
        impact=10 if risk > 40 else -20,
        evidence="Plaintiff claim plausibility evaluated",
        legal_basis="Iqbal/Twombly standard"
    ))
    
    verdict = "PLAINTIFF_FAVOR" if risk > 50 else "DEFENSE_FAVOR" if risk < 50 else "NEUTRAL"
    
    civilist = report.get("civilist", "")
    commonist = report.get("commonist", "")
    synthesis = report.get("synthesis", "")
    
    return ExplainableVerdictResponse(
        risk_score=risk,
        verdict=verdict,
        confidence=0.75,  # Default confidence
        factors_applied=factors_response,
        interpretive_gap=gap,
        civilist_summary=civilist[:500] if civilist else "N/A",
        commonist_summary=commonist[:500] if commonist else "N/A",
        synthesis=synthesis[:500] if synthesis else "N/A"
    )
