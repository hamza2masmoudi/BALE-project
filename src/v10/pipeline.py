"""
BALE V11 Pipeline
End-to-end contract analysis: Chunk -> Classify -> Graph -> Power -> Dispute -> Report

V11 Innovations:
1. Semantic Chunking (replaces regex)
2. Confidence Calibration (integrated into classifier)
3. Clause Rewrite Suggestions
4. Monte Carlo Risk Simulation
5. Cross-Contract Corpus Intelligence
"""
import re
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
import logging

from src.v10.classifier_v10 import EmbeddingClassifier, get_classifier, ClassificationResult
from src.v10.contract_graph import ContractGraph, ClauseNode, build_contract_graph, GraphAnalysis
from src.v10.power_analyzer import PowerAnalyzer, PowerAnalysis
from src.v10.dispute_predictor import DisputePredictor, DisputePrediction

logger = logging.getLogger("bale_v10_pipeline")


@dataclass
class V10Report:
    """Complete V10/V11 analysis report."""
    # Metadata
    contract_type: str
    total_clauses: int
    analysis_time_ms: int
    # Classification
    clause_classifications: List[Dict[str, Any]]
    # Graph Analysis
    graph: Dict[str, Any]
    # Power Analysis
    power: Dict[str, Any]
    # Dispute Prediction
    disputes: Dict[str, Any]
    # Overall
    overall_risk_score: float
    risk_level: str
    executive_summary: str
    # V11 Fields (optional)
    suggested_rewrites: Optional[List[Dict[str, Any]]] = None
    risk_simulation: Optional[Dict[str, Any]] = None
    corpus_comparison: Optional[Dict[str, Any]] = None
    engine_version: str = "V11"

    def to_dict(self) -> Dict:
        result = {
            "metadata": {
                "contract_type": self.contract_type,
                "total_clauses": self.total_clauses,
                "analysis_time_ms": self.analysis_time_ms,
                "engine_version": self.engine_version,
            },
            "classifications": self.clause_classifications,
            "graph_analysis": self.graph,
            "power_analysis": self.power,
            "dispute_prediction": self.disputes,
            "overall": {
                "risk_score": round(self.overall_risk_score, 1),
                "risk_level": self.risk_level,
                "executive_summary": self.executive_summary,
            },
        }
        # V11 optional fields
        if self.suggested_rewrites is not None:
            result["suggested_rewrites"] = self.suggested_rewrites
        if self.risk_simulation is not None:
            result["risk_simulation"] = self.risk_simulation
        if self.corpus_comparison is not None:
            result["corpus_comparison"] = self.corpus_comparison
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


class V10Pipeline:
    """
    The BALE V11 Contract Reasoning Pipeline.

    Architecture:
    1. CHUNK: Semantic chunking (or regex fallback)
    2. CLASSIFY: Embedding classification + confidence calibration
    3. GRAPH: Build clause relationship graph
    4. POWER: Analyze party power asymmetry
    5. DISPUTE: Predict dispute hotspots
    6. REWRITE: Suggest safer clause alternatives (V11)
    7. SIMULATE: Monte Carlo risk distribution (V11)
    8. COMPARE: Cross-contract corpus intelligence (V11)
    9. REPORT: Generate actionable output
    """

    def __init__(self, multilingual: bool = True):
        self.classifier = get_classifier(multilingual=multilingual)
        self.power_analyzer = PowerAnalyzer()
        self.dispute_predictor = DisputePredictor()
        # V11 components (lazy-loaded)
        self._rewrite_engine = None
        self._semantic_chunker = None
        self._risk_simulator = None
        self._corpus_intelligence = None

    def analyze(
        self,
        contract_text: str,
        contract_type: str = "MSA",
        # V11 options
        suggest_rewrites: bool = True,
        simulate_risk: bool = True,
        corpus_compare: bool = True,
        use_semantic_chunking: bool = True,
    ) -> V10Report:
        """
        Run full V11 analysis on a contract.

        Args:
            contract_text: Full contract text
            contract_type: Type of contract (MSA, NDA, SLA, etc.)
            suggest_rewrites: Generate clause rewrite suggestions
            simulate_risk: Run Monte Carlo risk simulation
            corpus_compare: Compare against learned corpus patterns
            use_semantic_chunking: Use semantic chunking instead of regex

        Returns:
            V10Report with all analysis results
        """
        start = time.time()

        # Step 1: CHUNK (V11: semantic chunking)
        if use_semantic_chunking:
            clauses = self._chunk_semantic(contract_text)
        else:
            clauses = self._chunk_contract(contract_text)
        logger.info(f"Chunked contract into {len(clauses)} clauses")

        # Step 2: CLASSIFY (V11: includes calibration automatically)
        classified = self._classify_clauses(clauses)
        logger.info(f"Classified {len(classified)} clauses")

        # Step 3: GRAPH
        graph, graph_analysis = build_contract_graph(classified, contract_type)
        logger.info(
            f"Built graph: {graph_analysis.conflict_count} conflicts, "
            f"{graph_analysis.dependency_gap_count} gaps"
        )

        # Step 4: POWER
        power_analysis = self.power_analyzer.analyze(classified, contract_text)
        logger.info(f"Power score: {power_analysis.power_score:.1f}")

        # Step 5: DISPUTE
        dispute_prediction = self.dispute_predictor.predict(
            graph_analysis, power_analysis, classified
        )
        logger.info(f"Predicted {len(dispute_prediction.hotspots)} dispute hotspots")

        # Step 6: Overall risk
        overall_risk = (
            graph_analysis.structural_risk * 0.3
            + power_analysis.power_score * 0.2
            + dispute_prediction.overall_dispute_risk * 0.5
        )
        overall_risk = min(100, overall_risk)

        if overall_risk >= 70:
            risk_level = "HIGH"
        elif overall_risk >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Step 7: V11 — Clause Rewrite Suggestions
        rewrite_data = None
        if suggest_rewrites:
            rewrite_data = self._suggest_rewrites(classified, dispute_prediction)

        # Step 8: V11 — Monte Carlo Risk Simulation
        simulation_data = None
        if simulate_risk:
            simulation_data = self._simulate_risk(
                classified, graph_analysis, power_analysis, dispute_prediction, overall_risk
            )

        # Step 9: V11 — Corpus Intelligence
        corpus_data = None

        # Generate summary
        summary = self._generate_summary(
            graph_analysis, power_analysis, dispute_prediction, risk_level
        )

        elapsed_ms = int((time.time() - start) * 1000)

        report = V10Report(
            contract_type=contract_type,
            total_clauses=len(classified),
            analysis_time_ms=elapsed_ms,
            clause_classifications=[
                {
                    "id": c["id"],
                    "clause_type": c["clause_type"],
                    "confidence": round(c["confidence"], 3),
                    "calibrated_confidence": round(c.get("calibrated_confidence", 0), 3),
                    "entropy_ratio": c.get("entropy_ratio", 0),
                    "margin": c.get("margin", 0),
                    "needs_human_review": c.get("needs_human_review", False),
                    "text_preview": c["text"][:100] + "...",
                    "risk_weight": c.get("risk_weight", 0.5),
                    "top_3": c.get("top_3", []),
                }
                for c in classified
            ],
            graph=graph_analysis.to_dict(),
            power=power_analysis.to_dict(),
            disputes=dispute_prediction.to_dict(),
            overall_risk_score=overall_risk,
            risk_level=risk_level,
            executive_summary=summary,
            suggested_rewrites=rewrite_data,
            risk_simulation=simulation_data,
            corpus_comparison=corpus_data,
            engine_version="V11",
        )

        # V11: Ingest into corpus for learning (after report built)
        if corpus_compare:
            try:
                corpus_data = self._corpus_compare(report)
                report.corpus_comparison = corpus_data
            except Exception as e:
                logger.warning(f"Corpus comparison failed: {e}")

        return report

    # ==================== V11 INNOVATIONS ====================

    def _chunk_semantic(self, text: str) -> List[Dict[str, str]]:
        """V11: Semantic chunking using embedding similarity."""
        try:
            if self._semantic_chunker is None:
                from src.v10.semantic_chunker import SemanticChunker
                self._semantic_chunker = SemanticChunker(
                    encoder=self.classifier.model
                )
            chunks = self._semantic_chunker.chunk(text)
            return [
                {
                    "id": chunk.id,
                    "text": chunk.text,
                    "header": chunk.header,
                }
                for chunk in chunks
            ]
        except Exception as e:
            logger.warning(f"Semantic chunking failed, falling back to regex: {e}")
            return self._chunk_contract(text)

    def _suggest_rewrites(
        self,
        classified: List[Dict[str, Any]],
        disputes: DisputePrediction,
    ) -> Optional[List[Dict[str, Any]]]:
        """V11: Suggest safer clause alternatives for high-risk clauses."""
        try:
            if self._rewrite_engine is None:
                from src.v10.rewrite_engine import RewriteEngine
                self._rewrite_engine = RewriteEngine(
                    encoder=self.classifier.model
                )

            # Build lookup of dispute probabilities by clause
            dispute_probs = {}
            for hotspot in disputes.hotspots:
                dispute_probs[hotspot.clause_type] = hotspot.dispute_probability

            # Find clauses needing rewrites
            suggestions = []
            for clause in classified:
                risk = dispute_probs.get(clause["clause_type"], 0) * 100
                if risk < 35:  # only suggest for medium+ risk
                    continue
                suggestion = self._rewrite_engine.suggest(
                    clause_text=clause["text"],
                    clause_type=clause["clause_type"],
                    current_risk=risk,
                )
                if suggestion:
                    suggestions.append(suggestion.to_dict())

            return suggestions if suggestions else None
        except Exception as e:
            logger.warning(f"Rewrite suggestions failed: {e}")
            return None

    def _simulate_risk(
        self,
        classified: List[Dict[str, Any]],
        graph_analysis: GraphAnalysis,
        power_analysis: PowerAnalysis,
        disputes: DisputePrediction,
        base_risk: float,
    ) -> Optional[Dict[str, Any]]:
        """V11: Monte Carlo risk simulation."""
        try:
            if self._risk_simulator is None:
                from src.v10.risk_simulator import RiskSimulator
                self._risk_simulator = RiskSimulator(n_simulations=1000)

            result = self._risk_simulator.simulate(
                classified_clauses=classified,
                graph_analysis_dict=graph_analysis.to_dict(),
                power_analysis_dict=power_analysis.to_dict(),
                dispute_analysis_dict=disputes.to_dict(),
                base_risk_score=base_risk,
            )
            return result.to_dict()
        except Exception as e:
            logger.warning(f"Risk simulation failed: {e}")
            return None

    def _corpus_compare(self, report: V10Report) -> Optional[Dict[str, Any]]:
        """V11: Compare against corpus and learn patterns."""
        try:
            if self._corpus_intelligence is None:
                from src.v10.corpus_intelligence import CorpusIntelligence
                self._corpus_intelligence = CorpusIntelligence()

            report_dict = report.to_dict()

            # First ingest, then compare
            self._corpus_intelligence.ingest(report_dict)
            comparison = self._corpus_intelligence.compare(report_dict)
            return comparison.to_dict()
        except Exception as e:
            logger.warning(f"Corpus comparison failed: {e}")
            return None

    # ==================== ORIGINAL V10 METHODS ====================

    def _chunk_contract(self, text: str) -> List[Dict[str, str]]:
        """
        Split a contract into individual clauses.
        Strategy: Split on TOP-LEVEL numbered sections only.
        """
        clauses = []
        top_level_pattern = r'(?=(?:^|\n)\s*(?:(?:Section|Article|Clause)\s+)?\d{1,2}\.\s+[A-Z])'
        sections = re.split(top_level_pattern, text, flags=re.IGNORECASE)

        if len(sections) > 3:
            for i, section in enumerate(sections):
                section = section.strip()
                if len(section) > 30:
                    first_line = section.split("\n")[0].strip()
                    clauses.append({
                        "id": f"section_{i}",
                        "text": section[:3000],
                        "header": first_line,
                    })
        else:
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for i, para in enumerate(paragraphs):
                if len(para) > 30:
                    clauses.append({
                        "id": f"clause_{i}",
                        "text": para[:2000],
                    })
        return clauses

    def _classify_clauses(self, clauses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Classify each clause with V11 calibration metrics."""
        texts = [c["text"] for c in clauses]
        results = self.classifier.classify_batch(texts)
        classified = []
        for clause, result in zip(clauses, results):
            classified.append({
                **clause,
                "clause_type": result.clause_type,
                "confidence": result.confidence,
                "calibrated_confidence": result.calibrated_confidence,
                "entropy_ratio": result.entropy_ratio,
                "margin": result.margin,
                "needs_human_review": result.needs_human_review,
                "top_3": result.top_3,
                "language": result.language_detected,
                "risk_weight": self.classifier.get_risk_weight(result.clause_type),
                "category": self.classifier.get_category(result.clause_type),
            })
        return classified

    def _generate_summary(
        self,
        graph: GraphAnalysis,
        power: PowerAnalysis,
        disputes: DisputePrediction,
        risk_level: str,
    ) -> str:
        """Generate a human-readable executive summary."""
        parts = []
        parts.append(f"Contract Risk Level: {risk_level}.")

        if graph.conflict_count > 0:
            parts.append(f"{graph.conflict_count} inter-clause conflict(s) detected.")
        if graph.dependency_gap_count > 0:
            parts.append(f"{graph.dependency_gap_count} missing clause dependency(ies).")
        if len(graph.missing_expected) > 0:
            top_missing = [
                m["clause_type"].replace("_", " ")
                for m in graph.missing_expected[:3]
            ]
            parts.append(f"Missing expected clauses: {', '.join(top_missing)}.")
        if power.power_score > 30:
            parts.append(
                f"Power imbalance detected (score: {power.power_score:.0f}/100): "
                f"{power.dominant_party} holds dominant position."
            )
        if disputes.hotspots:
            top = disputes.hotspots[0]
            parts.append(
                f"Highest dispute risk: {top.clause_type.replace('_', ' ')} "
                f"({top.dispute_probability:.0%} probability)."
            )
        parts.append(f"Completeness: {graph.completeness_score:.0%}.")
        return " ".join(parts)


# ==================== CONVENIENCE FUNCTIONS ====================


def analyze_contract(
    text: str,
    contract_type: str = "MSA",
    suggest_rewrites: bool = True,
    simulate_risk: bool = True,
    corpus_compare: bool = True,
) -> V10Report:
    """Quick analysis of a contract with all V11 innovations enabled."""
    pipeline = V10Pipeline(multilingual=True)
    return pipeline.analyze(
        text,
        contract_type,
        suggest_rewrites=suggest_rewrites,
        simulate_risk=simulate_risk,
        corpus_compare=corpus_compare,
    )


__all__ = ["V10Pipeline", "V10Report", "analyze_contract"]
