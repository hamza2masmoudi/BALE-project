"""
BALE V12 — Unified Quad-Innovation Engine
===========================================
Orchestrates all four V12 innovations into a single analysis pass:
    1. Neuro-Symbolic Legal Reasoning
    2. RAG Case Law Intelligence
    3. Graph Attention Network
    4. Multi-Agent Legal Debate

Produces a unified V12Report that fuses all four perspectives
into a single, deeply grounded contract risk assessment.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from src.v12.symbolic_reasoner import SymbolicReasoner, SymbolicVerdict
from src.v12.case_law_rag import CaseLawRAG, RAGResult
from src.v12.graph_attention import ContractGAT, GATScores
from src.v12.legal_debate import LegalDebateEngine, DebateTranscript

logger = logging.getLogger("bale_v12_engine")


# ==================== V12 REPORT ====================

@dataclass
class V12Report:
    """
    Unified V12 analysis report combining all four innovations.
    
    Extends V11's V10Report with:
    - Neuro-symbolic doctrine violations and fused risk
    - Case law citations with grounded rewrites
    - Learned graph risk scores from GAT
    - Full debate transcript with judicial rulings
    - Meta-fused risk score combining all four perspectives
    """
    # V11 base
    v11_contract_type: str
    v11_risk_score: float
    v11_clause_count: int

    # Innovation 1: Neuro-Symbolic
    symbolic_verdict: Optional[SymbolicVerdict] = None

    # Innovation 2: RAG Case Law
    case_law_results: Optional[RAGResult] = None

    # Innovation 3: Graph Attention Network
    gnn_scores: Optional[GATScores] = None

    # Innovation 4: Multi-Agent Debate
    debate_transcript: Optional[DebateTranscript] = None

    # V12 Meta-Fusion
    v12_fused_risk: float = 0.0
    v12_confidence: float = 0.0
    analysis_time_ms: int = 0
    engine_version: str = "V12"
    innovation_summary: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_version": self.engine_version,
            "v11_base": {
                "contract_type": self.v11_contract_type,
                "risk_score": self.v11_risk_score,
                "clause_count": self.v11_clause_count,
            },
            "symbolic_verdict": (
                self.symbolic_verdict.to_dict() if self.symbolic_verdict else None
            ),
            "case_law_results": (
                self.case_law_results.to_dict() if self.case_law_results else None
            ),
            "gnn_scores": (
                self.gnn_scores.to_dict() if self.gnn_scores else None
            ),
            "debate_transcript": (
                self.debate_transcript.to_dict() if self.debate_transcript else None
            ),
            "v12_fused_risk": round(self.v12_fused_risk, 2),
            "v12_confidence": round(self.v12_confidence, 3),
            "analysis_time_ms": self.analysis_time_ms,
            "innovation_summary": self.innovation_summary,
        }

    def to_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ==================== V12 ENGINE ====================

class V12Engine:
    """
    Unified V12 Engine — orchestrates all four innovations.
    
    Usage:
        engine = V12Engine()
        v12_report = engine.analyze(v11_report)
    """

    def __init__(self):
        self.symbolic_reasoner = SymbolicReasoner()
        self.case_law_rag = CaseLawRAG()
        self.gat = ContractGAT()
        self.debate_engine = LegalDebateEngine()
        logger.info("V12Engine initialized with all 4 innovations")

    def analyze(
        self,
        v11_report,
        enable_symbolic: bool = True,
        enable_rag: bool = True,
        enable_gnn: bool = True,
        enable_debate: bool = True,
    ) -> V12Report:
        """
        Run all four V12 innovations on a V11 report.
        
        Args:
            v11_report: V10Report from the V11 pipeline
            enable_symbolic: Enable neuro-symbolic reasoning
            enable_rag: Enable RAG case law retrieval
            enable_gnn: Enable Graph Attention Network
            enable_debate: Enable multi-agent legal debate
            
        Returns:
            V12Report with all innovation results fused
        """
        start = time.time()

        # Extract base info from V11
        v11_risk = getattr(v11_report, 'risk_score', 50.0)
        if isinstance(v11_risk, str):
            try:
                v11_risk = float(v11_risk)
            except (ValueError, TypeError):
                v11_risk = 50.0

        contract_type = getattr(v11_report, 'contract_type', 'MSA')
        clause_count = getattr(v11_report, 'total_clauses', 0)

        # Run innovations
        symbolic = None
        rag = None
        gnn = None
        debate = None
        summary = {}

        if enable_symbolic:
            try:
                symbolic = self.symbolic_reasoner.evaluate(v11_report)
                summary["symbolic"] = (
                    f"{symbolic.violations_triggered} doctrine violations found, "
                    f"symbolic risk: {symbolic.symbolic_risk_score:.1f}"
                )
                logger.info(f"Symbolic: {symbolic.violations_triggered} violations")
            except Exception as e:
                logger.error(f"Symbolic reasoning failed: {e}")
                summary["symbolic"] = f"Error: {str(e)[:100]}"

        if enable_rag:
            try:
                rag = self.case_law_rag.retrieve(v11_report)
                summary["rag"] = (
                    f"{rag.citations_retrieved} case citations retrieved "
                    f"from {rag.total_cases_searched} cases"
                )
                logger.info(f"RAG: {rag.citations_retrieved} citations")
            except Exception as e:
                logger.error(f"Case law RAG failed: {e}")
                summary["rag"] = f"Error: {str(e)[:100]}"

        if enable_gnn:
            try:
                gnn = self.gat.forward(v11_report)
                summary["gnn"] = (
                    f"Graph risk: {gnn.graph_risk_score:.1f}, "
                    f"anomaly: {gnn.structural_anomaly_score:.3f}"
                )
                logger.info(f"GNN: risk={gnn.graph_risk_score:.1f}")
            except Exception as e:
                logger.error(f"GNN failed: {e}")
                summary["gnn"] = f"Error: {str(e)[:100]}"

        if enable_debate:
            try:
                debate = self.debate_engine.debate(v11_report)
                summary["debate"] = (
                    f"Verdict: {debate.final_verdict}, "
                    f"{len(debate.rulings)} rulings"
                )
                logger.info(f"Debate: {debate.final_verdict}")
            except Exception as e:
                logger.error(f"Debate failed: {e}")
                summary["debate"] = f"Error: {str(e)[:100]}"

        # Meta-fusion: combine all risk perspectives
        fused_risk, confidence = self._meta_fuse(v11_risk, symbolic, gnn, debate)

        elapsed_ms = int((time.time() - start) * 1000)

        return V12Report(
            v11_contract_type=contract_type,
            v11_risk_score=v11_risk,
            v11_clause_count=clause_count,
            symbolic_verdict=symbolic,
            case_law_results=rag,
            gnn_scores=gnn,
            debate_transcript=debate,
            v12_fused_risk=fused_risk,
            v12_confidence=confidence,
            analysis_time_ms=elapsed_ms,
            innovation_summary=summary,
        )

    def _meta_fuse(
        self,
        v11_risk: float,
        symbolic: Optional[SymbolicVerdict],
        gnn: Optional[GATScores],
        debate: Optional[DebateTranscript],
    ) -> tuple:
        """
        Meta-fusion: combine risk scores from all available innovations.
        
        Weighting:
            - V11 neural: 25%
            - Symbolic fused: 25%
            - GNN graph: 25%
            - Debate adjustment: 25%
            
        Confidence is the agreement level between the perspectives.
        """
        scores = [v11_risk]
        weights = [0.25]

        if symbolic:
            scores.append(symbolic.fused_risk_score)
            weights.append(0.25)
        
        if gnn:
            scores.append(gnn.graph_risk_score)
            weights.append(0.25)

        if debate:
            # Debate adjusts from baseline rather than providing absolute score
            debate_adjusted = v11_risk + (debate.final_risk_adjustment * 100)
            debate_adjusted = max(0, min(100, debate_adjusted))
            scores.append(debate_adjusted)
            weights.append(0.25)

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Weighted average
        fused = sum(s * w for s, w in zip(scores, weights))
        fused = max(0, min(100, fused))

        # Confidence: measure agreement (inverse of score variance)
        if len(scores) > 1:
            import numpy as np
            variance = np.var(scores)
            max_variance = 2500  # max possible variance for [0,100]
            confidence = 1.0 - (variance / max_variance)
            confidence = max(0.1, min(0.99, confidence))
        else:
            confidence = 0.5

        return fused, confidence
