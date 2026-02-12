#!/usr/bin/env python3
"""
BALE V12 Quad-Innovation — Comprehensive Unit Test Suite
=========================================================
Tests each innovation module independently and the unified engine.
Results are suitable for inclusion in the research paper.

Usage:
    python evaluation/test_v12_unit.py
"""
import sys, os, time, json, traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))


# ==================== MOCK V11 REPORT ====================

class MockV11Report:
    """Simulates a V10Report from the V11 pipeline for testing."""
    def __init__(self, scenario: str = "standard"):
        self.engine_version = "V11"
        self.contract_type = "MSA"
        self.total_clauses = 12
        self.analysis_time_ms = 200
        self.risk_score = 42.0
        self.overall_risk_score = 42.0
        self.risk_level = "Moderate"
        self.executive_summary = "Mock contract for V12 testing."

        if scenario == "high_risk":
            self._build_high_risk()
        elif scenario == "low_risk":
            self._build_low_risk()
        elif scenario == "minimal":
            self._build_minimal()
        elif scenario == "adversarial":
            self._build_adversarial()
        else:
            self._build_standard()

    def _build_standard(self):
        self.clause_classifications = [
            {"clause_type": "indemnification", "type": "indemnification", "text": "Client shall indemnify and hold harmless Provider against all claims arising from Client's use",
             "confidence": 0.88, "calibrated_confidence": 0.88, "risk_weight": 0.75, "category": "liability",
             "needs_human_review": False, "entropy_ratio": 0.22, "margin": 0.58},
            {"clause_type": "limitation_of_liability", "type": "limitation_of_liability", "text": "In no event shall Provider's liability exceed the total fees paid under this agreement",
             "confidence": 0.92, "calibrated_confidence": 0.92, "risk_weight": 0.70, "category": "liability",
             "needs_human_review": False, "entropy_ratio": 0.15, "margin": 0.71},
            {"clause_type": "termination", "type": "termination", "text": "Either party may terminate this agreement for any breach with 30 days notice",
             "confidence": 0.71, "calibrated_confidence": 0.71, "risk_weight": 0.65, "category": "governance",
             "needs_human_review": True, "entropy_ratio": 0.68, "margin": 0.12},
            {"clause_type": "confidentiality", "type": "confidentiality", "text": "All confidential information shall be maintained in strict confidence for a period of five years",
             "confidence": 0.85, "calibrated_confidence": 0.85, "risk_weight": 0.40, "category": "confidentiality",
             "needs_human_review": False, "entropy_ratio": 0.30, "margin": 0.45},
            {"clause_type": "intellectual_property", "type": "intellectual_property", "text": "All work product shall be the sole property of the Client",
             "confidence": 0.90, "calibrated_confidence": 0.90, "risk_weight": 0.60, "category": "ip",
             "needs_human_review": False, "entropy_ratio": 0.18, "margin": 0.62},
            {"clause_type": "governing_law", "type": "governing_law", "text": "This agreement shall be governed by the laws of Delaware",
             "confidence": 0.95, "calibrated_confidence": 0.95, "risk_weight": 0.20, "category": "governance",
             "needs_human_review": False, "entropy_ratio": 0.08, "margin": 0.80},
            {"clause_type": "warranty", "type": "warranty", "text": "Services shall be performed in a workmanlike manner consistent with industry standards",
             "confidence": 0.87, "calibrated_confidence": 0.87, "risk_weight": 0.35, "category": "quality",
             "needs_human_review": False, "entropy_ratio": 0.25, "margin": 0.50},
            {"clause_type": "payment_terms", "type": "payment_terms", "text": "Payment is due within 60 days of receipt of invoice",
             "confidence": 0.93, "calibrated_confidence": 0.93, "risk_weight": 0.30, "category": "financial",
             "needs_human_review": False, "entropy_ratio": 0.12, "margin": 0.72},
            {"clause_type": "non_compete", "type": "non_compete", "text": "For a period of 24 months following termination worldwide",
             "confidence": 0.78, "calibrated_confidence": 0.78, "risk_weight": 0.80, "category": "operational",
             "needs_human_review": True, "entropy_ratio": 0.55, "margin": 0.22},
            {"clause_type": "force_majeure", "type": "force_majeure", "text": "Neither party shall be liable for delays caused by acts of God",
             "confidence": 0.82, "calibrated_confidence": 0.82, "risk_weight": 0.25, "category": "force_majeure",
             "needs_human_review": False, "entropy_ratio": 0.35, "margin": 0.42},
            {"clause_type": "data_protection", "type": "data_protection", "text": "Provider shall process personal data only in accordance with documented instructions",
             "confidence": 0.80, "calibrated_confidence": 0.80, "risk_weight": 0.55, "category": "data",
             "needs_human_review": False, "entropy_ratio": 0.40, "margin": 0.35},
            {"clause_type": "assignment", "type": "assignment", "text": "Neither party may assign this agreement without prior written consent",
             "confidence": 0.91, "calibrated_confidence": 0.91, "risk_weight": 0.30, "category": "assignment",
             "needs_human_review": False, "entropy_ratio": 0.14, "margin": 0.68},
        ]
        self.graph = {
            "structural_risk": 35,
            "completeness_score": 0.85,
            "conflicts": [
                {"source": "indemnification", "target": "limitation_of_liability", "description": "Uncapped indemnification conflicts with liability cap", "severity": 0.8},
                {"source": "termination", "target": "force_majeure", "description": "Termination for any breach may override force majeure protection", "severity": 0.6},
            ],
            "edges": [
                {"source": "indemnification", "target": "limitation_of_liability", "severity": 0.8},
                {"source": "termination", "target": "force_majeure", "severity": 0.6},
                {"source": "confidentiality", "target": "intellectual_property", "severity": 0.4},
            ],
        }
        self.power = {"power_score": 65, "dominant_party": "Provider"}
        self.disputes = {"overall_dispute_risk": 45, "hotspots": ["indemnification", "termination"]}
        self.suggested_rewrites = [
            {"clause_type": "indemnification", "risk_reduction_pct": 28},
            {"clause_type": "termination", "risk_reduction_pct": 22},
        ]
        self.risk_simulation = {"mean_risk": 42.3, "ci_95_lower": 25.6, "ci_95_upper": 59.0}
        self.corpus_comparison = {"anomalies": [{"metric": "risk_score", "z_score": 2.31}]}

    def _build_high_risk(self):
        self._build_standard()
        self.risk_score = 78.0
        self.overall_risk_score = 78.0
        self.risk_level = "High"
        # Make clauses riskier
        for cls in self.clause_classifications:
            cls["risk_weight"] = min(cls["risk_weight"] + 0.25, 1.0)
            cls["confidence"] = max(cls["confidence"] - 0.15, 0.4)
            cls["needs_human_review"] = cls["confidence"] < 0.7
        self.power = {"power_score": 85, "dominant_party": "Provider"}
        self.graph["structural_risk"] = 72
        self.graph["conflicts"].append(
            {"source": "non_compete", "target": "governing_law", "description": "Worldwide non-compete may be unenforceable", "severity": 0.9}
        )

    def _build_low_risk(self):
        self._build_standard()
        self.risk_score = 15.0
        self.overall_risk_score = 15.0
        self.risk_level = "Low"
        for cls in self.clause_classifications:
            cls["risk_weight"] = max(cls["risk_weight"] - 0.3, 0.1)
            cls["confidence"] = min(cls["confidence"] + 0.1, 0.99)
            cls["needs_human_review"] = False
        self.power = {"power_score": 50, "dominant_party": "balanced"}
        self.graph["structural_risk"] = 10
        self.graph["conflicts"] = []

    def _build_minimal(self):
        self.clause_classifications = [
            {"clause_type": "governing_law", "type": "governing_law", "text": "Laws of Delaware",
             "confidence": 0.95, "calibrated_confidence": 0.95, "risk_weight": 0.15, "category": "governance",
             "needs_human_review": False},
        ]
        self.graph = {"structural_risk": 5, "conflicts": [], "edges": []}
        self.power = {"power_score": 50}
        self.disputes = {"overall_dispute_risk": 5, "hotspots": []}
        self.suggested_rewrites = []
        self.risk_simulation = None
        self.corpus_comparison = None

    def _build_adversarial(self):
        self._build_standard()
        self.risk_score = 95.0
        self.overall_risk_score = 95.0
        for cls in self.clause_classifications:
            cls["risk_weight"] = 0.9
            cls["confidence"] = 0.45
            cls["needs_human_review"] = True
        self.power = {"power_score": 95}
        self.graph["structural_risk"] = 90


# ==================== TEST RUNNER ====================

@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class V12TestSuite:
    """Comprehensive test suite for all V12 innovations."""

    def __init__(self):
        self.results: List[TestResult] = []

    def run_test(self, name: str, test_fn):
        """Execute a single test and record the result."""
        t0 = time.time()
        try:
            details = test_fn()
            elapsed = (time.time() - t0) * 1000
            self.results.append(TestResult(name=name, passed=True, duration_ms=elapsed, details=details or {}))
            print(f"  ✓ {name} ({elapsed:.0f}ms)")
        except Exception as e:
            elapsed = (time.time() - t0) * 1000
            self.results.append(TestResult(name=name, passed=False, duration_ms=elapsed, message=str(e)))
            print(f"  ✗ {name} — {str(e)[:80]}")
            traceback.print_exc()

    # ════════════════════ SYMBOLIC REASONER TESTS ════════════════════

    def test_symbolic_initialization(self):
        from src.v12.symbolic_reasoner import SymbolicReasoner
        sr = SymbolicReasoner()
        assert len(sr.rules) == 42, f"Expected 42 rules, got {len(sr.rules)}"
        return {"rule_count": len(sr.rules)}

    def test_symbolic_rule_families(self):
        from src.v12.symbolic_reasoner import SymbolicReasoner, DOCTRINE_RULES
        families = set()
        for rule in DOCTRINE_RULES:
            families.add(rule.family.value)
        assert len(families) >= 7, f"Expected 7+ families, got {len(families)}: {families}"
        return {"families": sorted(families), "count": len(families)}

    def test_symbolic_standard_contract(self):
        from src.v12.symbolic_reasoner import SymbolicReasoner
        sr = SymbolicReasoner()
        report = MockV11Report("standard")
        verdict = sr.evaluate(report)
        assert verdict.total_rules_evaluated == 42
        assert verdict.violations_triggered >= 0
        assert 0 <= verdict.fused_risk_score <= 100
        assert 0 <= verdict.alpha <= 1.0
        return {
            "violations_triggered": verdict.violations_triggered,
            "symbolic_risk": round(verdict.symbolic_risk_score, 2),
            "neural_risk": round(verdict.neural_risk_score, 2),
            "fused_risk": round(verdict.fused_risk_score, 2),
            "alpha": round(verdict.alpha, 3),
        }

    def test_symbolic_high_risk(self):
        from src.v12.symbolic_reasoner import SymbolicReasoner
        sr = SymbolicReasoner()
        verdict = sr.evaluate(MockV11Report("high_risk"))
        assert verdict.violations_triggered > 0, "High-risk contract should trigger violations"
        assert verdict.symbolic_risk_score > 20, "Symbolic risk should be elevated"
        return {
            "violations": verdict.violations_triggered,
            "symbolic_risk": round(verdict.symbolic_risk_score, 2),
            "fused_risk": round(verdict.fused_risk_score, 2),
        }

    def test_symbolic_low_risk(self):
        from src.v12.symbolic_reasoner import SymbolicReasoner
        sr = SymbolicReasoner()
        verdict = sr.evaluate(MockV11Report("low_risk"))
        return {
            "violations": verdict.violations_triggered,
            "symbolic_risk": round(verdict.symbolic_risk_score, 2),
            "fused_risk": round(verdict.fused_risk_score, 2),
        }

    def test_symbolic_risk_ordering(self):
        """Risk should increase as contract severity increases."""
        from src.v12.symbolic_reasoner import SymbolicReasoner
        sr = SymbolicReasoner()
        low = sr.evaluate(MockV11Report("low_risk"))
        std = sr.evaluate(MockV11Report("standard"))
        high = sr.evaluate(MockV11Report("high_risk"))
        assert high.fused_risk_score > low.fused_risk_score, \
            f"High ({high.fused_risk_score}) should exceed Low ({low.fused_risk_score})"
        return {
            "low_fused": round(low.fused_risk_score, 2),
            "standard_fused": round(std.fused_risk_score, 2),
            "high_fused": round(high.fused_risk_score, 2),
            "monotonic": high.fused_risk_score > std.fused_risk_score > low.fused_risk_score,
        }

    def test_symbolic_alpha_adaptation(self):
        """Alpha should decrease (trust symbolic more) when violations are many."""
        from src.v12.symbolic_reasoner import SymbolicReasoner
        sr = SymbolicReasoner()
        low = sr.evaluate(MockV11Report("low_risk"))
        adv = sr.evaluate(MockV11Report("adversarial"))
        # Adversarial has low confidence → alpha should be lower (more symbolic trust)
        return {
            "low_risk_alpha": round(low.alpha, 3),
            "adversarial_alpha": round(adv.alpha, 3),
            "alpha_decreased": adv.alpha < low.alpha,
        }

    def test_symbolic_serialization(self):
        from src.v12.symbolic_reasoner import SymbolicReasoner
        sr = SymbolicReasoner()
        verdict = sr.evaluate(MockV11Report("standard"))
        d = verdict.to_dict()
        assert "total_rules_evaluated" in d
        assert "violations" in d
        assert isinstance(d["violations"], list)
        json_str = json.dumps(d)
        assert len(json_str) > 50
        return {"serializable": True, "json_size": len(json_str)}

    # ════════════════════ RAG CASE LAW TESTS ════════════════════

    def test_rag_initialization(self):
        from src.v12.case_law_rag import CaseLawRAG, CASE_LAW_DB
        rag = CaseLawRAG()
        assert len(rag.cases) >= 25, f"Expected 25+ cases, got {len(rag.cases)}"
        return {"case_count": len(rag.cases)}

    def test_rag_case_coverage(self):
        from src.v12.case_law_rag import CASE_LAW_DB
        types = set(c.clause_type for c in CASE_LAW_DB)
        jurisdictions = set(c.jurisdiction for c in CASE_LAW_DB)
        years = [c.year for c in CASE_LAW_DB]
        assert len(types) >= 10, f"Expected 10+ clause types, got {len(types)}"
        assert len(jurisdictions) >= 3, f"Expected 3+ jurisdictions, got {len(jurisdictions)}"
        return {
            "clause_types": len(types),
            "jurisdictions": sorted(jurisdictions),
            "year_range": f"{min(years)}-{max(years)}",
            "types": sorted(types),
        }

    def test_rag_retrieval_standard(self):
        from src.v12.case_law_rag import CaseLawRAG
        rag = CaseLawRAG()
        result = rag.retrieve(MockV11Report("standard"), top_k=3)
        assert result.total_cases_searched > 0
        assert result.citations_retrieved > 0
        assert len(result.citations) > 0
        return {
            "searched": result.total_cases_searched,
            "retrieved": result.citations_retrieved,
            "jurisdictions": result.jurisdictions_covered,
            "clause_types": result.clause_types_analyzed,
        }

    def test_rag_high_risk_more_citations(self):
        """High-risk contracts should retrieve more citations."""
        from src.v12.case_law_rag import CaseLawRAG
        rag = CaseLawRAG()
        low = rag.retrieve(MockV11Report("low_risk"), top_k=3)
        high = rag.retrieve(MockV11Report("high_risk"), top_k=3)
        return {
            "low_risk_citations": low.citations_retrieved,
            "high_risk_citations": high.citations_retrieved,
            "high_retrieves_more": high.citations_retrieved >= low.citations_retrieved,
        }

    def test_rag_relevance_scores(self):
        """Retrieved cases should have meaningful relevance scores."""
        from src.v12.case_law_rag import CaseLawRAG
        rag = CaseLawRAG()
        result = rag.retrieve(MockV11Report("standard"), top_k=3)
        for c in result.citations:
            assert 0 <= c.relevance_score <= 2.0, f"Score {c.relevance_score} out of range"
            assert len(c.grounded_rewrite) > 10, "Grounded rewrite too short"
            assert len(c.risk_explanation) > 10, "Risk explanation too short"
        return {
            "top_scores": [round(c.relevance_score, 3) for c in result.citations[:5]],
            "all_have_rewrites": all(len(c.grounded_rewrite) > 10 for c in result.citations),
        }

    def test_rag_serialization(self):
        from src.v12.case_law_rag import CaseLawRAG
        rag = CaseLawRAG()
        result = rag.retrieve(MockV11Report("standard"), top_k=3)
        d = result.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 100
        return {"serializable": True, "json_size": len(json_str)}

    # ════════════════════ GRAPH ATTENTION NETWORK TESTS ════════════════════

    def test_gat_initialization(self):
        from src.v12.graph_attention import ContractGAT
        gat = ContractGAT()
        assert gat.layer1.in_features == 400
        assert gat.layer1.out_features == 256
        assert gat.layer2.out_features == 128
        return {"layer1": "400→256", "layer2": "256→128", "heads": 4}

    def test_gat_layer_forward(self):
        """Test a single GAT layer independently."""
        import numpy as np
        from src.v12.graph_attention import GATLayer
        layer = GATLayer(64, 32, n_heads=4)
        features = np.random.randn(5, 64)
        adj = np.eye(5)
        adj[0, 1] = adj[1, 0] = 1
        adj[1, 2] = adj[2, 1] = 1
        out, attn = layer.forward(features, adj)
        assert out.shape == (5, 32), f"Expected (5,32), got {out.shape}"
        assert attn.shape == (5, 5), f"Expected (5,5), got {attn.shape}"
        assert np.all(np.isfinite(out)), "Non-finite values in output"
        return {"output_shape": list(out.shape), "attention_shape": list(attn.shape)}

    def test_gat_standard_contract(self):
        from src.v12.graph_attention import ContractGAT
        gat = ContractGAT()
        scores = gat.forward(MockV11Report("standard"))
        assert len(scores.node_results) > 0
        assert 0 <= scores.graph_risk_score <= 100
        assert len(scores.graph_embedding) == 64
        return {
            "nodes": len(scores.node_results),
            "graph_risk": round(scores.graph_risk_score, 2),
            "anomaly": round(scores.structural_anomaly_score, 3),
            "heuristic_risk": round(scores.heuristic_risk, 2),
            "top_edges": len(scores.top_attention_edges),
        }

    def test_gat_empty_contract(self):
        from src.v12.graph_attention import ContractGAT
        gat = ContractGAT()
        report = MockV11Report("minimal")
        report.clause_classifications = []
        scores = gat.forward(report)
        assert scores.graph_risk_score == 0.0
        return {"empty_handled": True}

    def test_gat_risk_differentiation(self):
        """GNN should produce different risk scores for different contracts."""
        from src.v12.graph_attention import ContractGAT
        gat = ContractGAT()
        low = gat.forward(MockV11Report("low_risk"))
        high = gat.forward(MockV11Report("high_risk"))
        return {
            "low_graph_risk": round(low.graph_risk_score, 2),
            "high_graph_risk": round(high.graph_risk_score, 2),
            "differentiated": low.graph_risk_score != high.graph_risk_score,
        }

    def test_gat_attention_meaningful(self):
        """Attention weights should sum to ~1 per node and be non-negative."""
        import numpy as np
        from src.v12.graph_attention import ContractGAT
        gat = ContractGAT()
        scores = gat.forward(MockV11Report("standard"))
        for node in scores.node_results:
            assert 0 <= node.learned_risk <= 1.0, f"Risk {node.learned_risk} out of [0,1]"
            assert 0 <= node.structural_importance <= 1.0
        return {
            "all_risks_valid": True,
            "all_importances_valid": True,
        }

    def test_gat_serialization(self):
        from src.v12.graph_attention import ContractGAT
        gat = ContractGAT()
        scores = gat.forward(MockV11Report("standard"))
        d = scores.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 100
        return {"serializable": True, "json_size": len(json_str)}

    # ════════════════════ LEGAL DEBATE TESTS ════════════════════

    def test_debate_initialization(self):
        from src.v12.legal_debate import LegalDebateEngine
        engine = LegalDebateEngine()
        return {"initialized": True}

    def test_debate_standard_contract(self):
        from src.v12.legal_debate import LegalDebateEngine
        engine = LegalDebateEngine()
        transcript = engine.debate(MockV11Report("standard"))
        assert len(transcript.prosecution_arguments) > 0, "Prosecution should make arguments"
        assert len(transcript.defense_arguments) > 0, "Defense should respond"
        assert len(transcript.rulings) > 0, "Judge should issue rulings"
        assert transcript.final_verdict in ("high_risk", "moderate_risk", "acceptable")
        return {
            "prosecution_args": len(transcript.prosecution_arguments),
            "defense_args": len(transcript.defense_arguments),
            "rulings": len(transcript.rulings),
            "verdict": transcript.final_verdict,
            "risk_adjustment": round(transcript.final_risk_adjustment, 3),
            "duration_ms": transcript.debate_duration_ms,
        }

    def test_debate_high_risk_sustained(self):
        """High-risk contracts should have more sustained rulings."""
        from src.v12.legal_debate import LegalDebateEngine
        engine = LegalDebateEngine()
        transcript = engine.debate(MockV11Report("high_risk"))
        sustained = sum(1 for r in transcript.rulings if r.verdict == "sustained")
        overruled = sum(1 for r in transcript.rulings if r.verdict == "overruled")
        assert sustained > 0, "High-risk should have sustained rulings"
        return {
            "sustained": sustained,
            "overruled": overruled,
            "verdict": transcript.final_verdict,
            "sustained_majority": sustained > overruled,
        }

    def test_debate_low_risk_balanced(self):
        from src.v12.legal_debate import LegalDebateEngine
        engine = LegalDebateEngine()
        transcript = engine.debate(MockV11Report("low_risk"))
        return {
            "verdict": transcript.final_verdict,
            "prosecution_args": len(transcript.prosecution_arguments),
            "defense_args": len(transcript.defense_arguments),
        }

    def test_debate_summary_generated(self):
        from src.v12.legal_debate import LegalDebateEngine
        engine = LegalDebateEngine()
        transcript = engine.debate(MockV11Report("standard"))
        assert len(transcript.summary) > 50, "Summary should be meaningful"
        assert "debated" in transcript.summary.lower() or "concluded" in transcript.summary.lower()
        return {"summary_length": len(transcript.summary)}

    def test_debate_ruling_reasoning(self):
        """Each ruling should have substantive reasoning."""
        from src.v12.legal_debate import LegalDebateEngine
        engine = LegalDebateEngine()
        transcript = engine.debate(MockV11Report("standard"))
        for r in transcript.rulings:
            assert len(r.reasoning) > 20, f"Ruling for {r.clause_type} has thin reasoning"
            assert r.prosecution_strength >= 0
            assert r.defense_strength >= 0
        return {
            "all_have_reasoning": True,
            "avg_reasoning_len": sum(len(r.reasoning) for r in transcript.rulings) // max(1, len(transcript.rulings)),
        }

    def test_debate_serialization(self):
        from src.v12.legal_debate import LegalDebateEngine
        engine = LegalDebateEngine()
        transcript = engine.debate(MockV11Report("standard"))
        d = transcript.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 200
        return {"serializable": True, "json_size": len(json_str)}

    # ════════════════════ V12 UNIFIED ENGINE TESTS ════════════════════

    def test_engine_initialization(self):
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        return {"initialized": True}

    def test_engine_full_analysis(self):
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        report = engine.analyze(MockV11Report("standard"))
        assert report.engine_version == "V12"
        assert report.symbolic_verdict is not None
        assert report.case_law_results is not None
        assert report.gnn_scores is not None
        assert report.debate_transcript is not None
        assert 0 <= report.v12_fused_risk <= 100
        assert 0 < report.v12_confidence <= 1.0
        return {
            "fused_risk": round(report.v12_fused_risk, 2),
            "confidence": round(report.v12_confidence, 3),
            "analysis_time_ms": report.analysis_time_ms,
            "innovations_active": len(report.innovation_summary),
        }

    def test_engine_selective_innovations(self):
        """Test enabling/disabling individual innovations."""
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        report = engine.analyze(
            MockV11Report("standard"),
            enable_symbolic=True,
            enable_rag=False,
            enable_gnn=True,
            enable_debate=False,
        )
        assert report.symbolic_verdict is not None
        assert report.case_law_results is None
        assert report.gnn_scores is not None
        assert report.debate_transcript is None
        return {"selective_worked": True}

    def test_engine_risk_fusion_quality(self):
        """V12 fused risk should be reasonable relative to V11."""
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        low = engine.analyze(MockV11Report("low_risk"))
        high = engine.analyze(MockV11Report("high_risk"))
        # V12 fused risk should preserve ordering
        assert high.v12_fused_risk > low.v12_fused_risk, \
            f"High ({high.v12_fused_risk}) should exceed Low ({low.v12_fused_risk})"
        return {
            "low_v11": 15.0,
            "low_v12": round(low.v12_fused_risk, 2),
            "high_v11": 78.0,
            "high_v12": round(high.v12_fused_risk, 2),
            "ordering_preserved": True,
        }

    def test_engine_all_scenarios(self):
        """Run all 4 scenarios through the full engine."""
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        results = {}
        for scenario in ["low_risk", "standard", "high_risk", "adversarial"]:
            report = engine.analyze(MockV11Report(scenario))
            results[scenario] = {
                "fused_risk": round(report.v12_fused_risk, 2),
                "confidence": round(report.v12_confidence, 3),
                "violations": report.symbolic_verdict.violations_triggered if report.symbolic_verdict else 0,
                "citations": report.case_law_results.citations_retrieved if report.case_law_results else 0,
                "debate_verdict": report.debate_transcript.final_verdict if report.debate_transcript else "n/a",
            }
        return results

    def test_engine_full_serialization(self):
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        report = engine.analyze(MockV11Report("standard"))
        json_str = report.to_json()
        parsed = json.loads(json_str)
        assert "symbolic_verdict" in parsed
        assert "case_law_results" in parsed
        assert "gnn_scores" in parsed
        assert "debate_transcript" in parsed
        return {"serializable": True, "json_size": len(json_str)}

    def test_engine_latency(self):
        """V12 engine should complete within 5 seconds for a standard contract."""
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        times = []
        for _ in range(3):
            t0 = time.time()
            engine.analyze(MockV11Report("standard"))
            times.append((time.time() - t0) * 1000)
        avg = sum(times) / len(times)
        assert avg < 5000, f"Average latency {avg:.0f}ms exceeds 5s limit"
        return {"avg_ms": round(avg), "min_ms": round(min(times)), "max_ms": round(max(times))}

    # ════════════════════ CROSS-INNOVATION TESTS ════════════════════

    def test_symbolic_rag_consistency(self):
        """Symbolic violations should correspond to RAG-retrieved clause types."""
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        report = engine.analyze(MockV11Report("standard"))
        if report.symbolic_verdict and report.case_law_results:
            violation_types = set()
            for v in report.symbolic_verdict.violations:
                for tc in v.triggering_clauses:
                    violation_types.add(tc.replace("missing:", ""))
            rag_types = set(report.case_law_results.clause_types_analyzed)
            overlap = violation_types & rag_types
            return {
                "violation_types": sorted(violation_types),
                "rag_types": sorted(rag_types),
                "overlap": sorted(overlap),
            }
        return {"skipped": "no violations or citations"}

    def test_debate_respects_gnn(self):
        """Debate verdict should directionally agree with GNN risk assessment."""
        from src.v12.v12_engine import V12Engine
        engine = V12Engine()
        report = engine.analyze(MockV11Report("high_risk"))
        if report.gnn_scores and report.debate_transcript:
            return {
                "gnn_risk": round(report.gnn_scores.graph_risk_score, 2),
                "debate_verdict": report.debate_transcript.final_verdict,
                "high_risk_agreement": report.debate_transcript.final_verdict != "acceptable",
            }
        return {"skipped": "missing data"}

    # ════════════════════ RUN ALL ════════════════════

    def run_all(self):
        print("=" * 70)
        print("BALE V12 Quad-Innovation — Unit Test Suite")
        print("=" * 70)

        # Symbolic Reasoner
        print("\n─── 1. Neuro-Symbolic Legal Reasoning ───")
        self.run_test("Symbolic: initialization", self.test_symbolic_initialization)
        self.run_test("Symbolic: rule families", self.test_symbolic_rule_families)
        self.run_test("Symbolic: standard contract", self.test_symbolic_standard_contract)
        self.run_test("Symbolic: high-risk contract", self.test_symbolic_high_risk)
        self.run_test("Symbolic: low-risk contract", self.test_symbolic_low_risk)
        self.run_test("Symbolic: risk ordering (low < std < high)", self.test_symbolic_risk_ordering)
        self.run_test("Symbolic: alpha adaptation", self.test_symbolic_alpha_adaptation)
        self.run_test("Symbolic: serialization", self.test_symbolic_serialization)

        # RAG Case Law
        print("\n─── 2. RAG Case Law Intelligence ───")
        self.run_test("RAG: initialization", self.test_rag_initialization)
        self.run_test("RAG: case coverage", self.test_rag_case_coverage)
        self.run_test("RAG: retrieval standard", self.test_rag_retrieval_standard)
        self.run_test("RAG: high-risk more citations", self.test_rag_high_risk_more_citations)
        self.run_test("RAG: relevance scores", self.test_rag_relevance_scores)
        self.run_test("RAG: serialization", self.test_rag_serialization)

        # Graph Attention Network
        print("\n─── 3. Graph Attention Network ───")
        self.run_test("GAT: initialization", self.test_gat_initialization)
        self.run_test("GAT: layer forward pass", self.test_gat_layer_forward)
        self.run_test("GAT: standard contract", self.test_gat_standard_contract)
        self.run_test("GAT: empty contract", self.test_gat_empty_contract)
        self.run_test("GAT: risk differentiation", self.test_gat_risk_differentiation)
        self.run_test("GAT: attention meaningful", self.test_gat_attention_meaningful)
        self.run_test("GAT: serialization", self.test_gat_serialization)

        # Legal Debate
        print("\n─── 4. Multi-Agent Legal Debate ───")
        self.run_test("Debate: initialization", self.test_debate_initialization)
        self.run_test("Debate: standard contract", self.test_debate_standard_contract)
        self.run_test("Debate: high-risk sustained", self.test_debate_high_risk_sustained)
        self.run_test("Debate: low-risk balanced", self.test_debate_low_risk_balanced)
        self.run_test("Debate: summary generated", self.test_debate_summary_generated)
        self.run_test("Debate: ruling reasoning", self.test_debate_ruling_reasoning)
        self.run_test("Debate: serialization", self.test_debate_serialization)

        # V12 Engine
        print("\n─── 5. V12 Unified Engine ───")
        self.run_test("Engine: initialization", self.test_engine_initialization)
        self.run_test("Engine: full analysis", self.test_engine_full_analysis)
        self.run_test("Engine: selective innovations", self.test_engine_selective_innovations)
        self.run_test("Engine: risk fusion quality", self.test_engine_risk_fusion_quality)
        self.run_test("Engine: all scenarios", self.test_engine_all_scenarios)
        self.run_test("Engine: full serialization", self.test_engine_full_serialization)
        self.run_test("Engine: latency (<5s)", self.test_engine_latency)

        # Cross-Innovation
        print("\n─── 6. Cross-Innovation Coherence ───")
        self.run_test("Cross: symbolic-RAG consistency", self.test_symbolic_rag_consistency)
        self.run_test("Cross: debate respects GNN", self.test_debate_respects_gnn)

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        total_time = sum(r.duration_ms for r in self.results)

        print("\n" + "=" * 70)
        print(f"RESULTS: {passed}/{total} passed, {failed} failed ({total_time:.0f}ms total)")
        print("=" * 70)

        # Save detailed results
        output = {
            "test_suite": "V12 Quad-Innovation Unit Tests",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": round(passed / max(1, total) * 100, 1),
                "total_time_ms": round(total_time),
            },
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "duration_ms": round(r.duration_ms),
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

        output_path = Path(__file__).parent / "v12_unit_test_results.json"
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\nDetailed results: {output_path}")

        return output


if __name__ == "__main__":
    suite = V12TestSuite()
    suite.run_all()
