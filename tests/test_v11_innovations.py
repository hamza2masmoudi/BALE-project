"""
BALE V11 Innovation Tests
Tests for all 5 V11 innovations:
1. Clause Rewrite Engine
2. Confidence Calibration
3. Semantic Chunking
4. Monte Carlo Risk Simulation
5. Corpus Intelligence
"""
import pytest
import numpy as np
import sys
import os

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ==================== INNOVATION 1: REWRITE ENGINE ====================

class TestRewriteEngine:
    """Test clause rewrite suggestions."""

    def test_templates_exist_for_all_clause_types(self):
        from src.v10.rewrite_engine import CLAUSE_TEMPLATES
        expected_types = [
            "indemnification", "limitation_of_liability", "termination",
            "confidentiality", "intellectual_property", "governing_law",
            "data_protection", "warranty", "payment_terms", "non_compete",
            "dispute_resolution", "insurance", "audit_rights",
            "force_majeure", "scope_of_work",
        ]
        for ct in expected_types:
            assert ct in CLAUSE_TEMPLATES, f"Missing templates for {ct}"
            assert len(CLAUSE_TEMPLATES[ct]) >= 4, f"Need >= 4 templates for {ct}"

    def test_each_template_has_required_fields(self):
        from src.v10.rewrite_engine import CLAUSE_TEMPLATES
        for ct, templates in CLAUSE_TEMPLATES.items():
            for i, t in enumerate(templates):
                assert "level" in t, f"Template {i} for {ct} missing 'level'"
                assert "text" in t, f"Template {i} for {ct} missing 'text'"
                assert "risk_score" in t, f"Template {i} for {ct} missing 'risk_score'"
                assert len(t["text"]) > 50, f"Template {i} for {ct} text is too short"

    def test_suggest_returns_valid_result(self):
        """Test that the engine returns a valid suggestion for a risky clause."""
        from src.v10.rewrite_engine import RewriteEngine

        engine = RewriteEngine()
        risky_text = (
            "The vendor shall be solely and exclusively liable for any and all "
            "damages, losses, costs, and expenses of whatever nature arising from "
            "any breach of this agreement, without any limitation whatsoever."
        )
        suggestion = engine.suggest(
            clause_text=risky_text,
            clause_type="limitation_of_liability",
            current_risk=80.0,
        )
        assert suggestion is not None
        assert suggestion.risk_reduction > 0
        assert suggestion.suggested_risk_score < 80
        assert len(suggestion.suggested_text) > 50
        assert suggestion.explanation is not None

    def test_suggest_returns_none_for_unknown_type(self):
        from src.v10.rewrite_engine import RewriteEngine

        engine = RewriteEngine()
        result = engine.suggest("some text", "unknown_type", 50)
        assert result is None

    def test_batch_suggestions(self):
        from src.v10.rewrite_engine import RewriteEngine

        engine = RewriteEngine()
        clauses = [
            {"text": "The client must indemnify against all claims forever.", "clause_type": "indemnification", "dispute_probability": 0.7},
            {"text": "Payment is due.", "clause_type": "payment_terms", "dispute_probability": 0.1},
        ]
        suggestions = engine.suggest_batch(clauses, risk_threshold=40.0)
        # Should only return suggestion for the high-risk clause
        assert len(suggestions) >= 1
        assert suggestions[0].clause_type == "indemnification"


# ==================== INNOVATION 2: CONFIDENCE CALIBRATION ====================

class TestConfidenceCalibration:
    """Test Bayesian confidence calibration."""

    def test_calibrator_produces_valid_probabilities(self):
        from src.v10.classifier_v10 import ConfidenceCalibrator
        cal = ConfidenceCalibrator()
        similarities = np.array([0.7, 0.3, 0.1, 0.05, 0.02])
        probs = cal.calibrate(similarities)
        assert abs(np.sum(probs) - 1.0) < 1e-6, "Probabilities must sum to 1"
        assert np.all(probs >= 0), "All probabilities must be non-negative"

    def test_entropy_ratio_range(self):
        from src.v10.classifier_v10 import ConfidenceCalibrator
        cal = ConfidenceCalibrator()

        # Certain distribution
        certain = np.array([0.99, 0.005, 0.005])
        entropy = cal.compute_entropy_ratio(certain)
        assert 0 <= entropy <= 1

        # Uncertain distribution
        uniform = np.array([0.33, 0.33, 0.34])
        entropy_high = cal.compute_entropy_ratio(uniform)
        assert entropy_high > entropy, "Uniform should have higher entropy"

    def test_margin_computation(self):
        from src.v10.classifier_v10 import ConfidenceCalibrator
        cal = ConfidenceCalibrator()

        # Clear winner
        margin = cal.compute_margin(np.array([0.8, 0.15, 0.05]))
        assert margin > 0.5

        # Ambiguous
        margin_low = cal.compute_margin(np.array([0.35, 0.33, 0.32]))
        assert margin_low < 0.05

    def test_needs_review_flag(self):
        from src.v10.classifier_v10 import ConfidenceCalibrator
        cal = ConfidenceCalibrator()
        # High entropy, low margin -> needs review
        assert cal.needs_review(margin=0.03, entropy_ratio=0.8) is True
        # Low entropy, high margin -> no review
        assert cal.needs_review(margin=0.3, entropy_ratio=0.4) is False

    def test_classification_includes_calibrated_fields(self):
        from src.v10.classifier_v10 import get_classifier, reset_classifier
        reset_classifier()
        classifier = get_classifier(multilingual=True)
        result = classifier.classify("This contract shall be governed by the laws of France.")
        assert hasattr(result, "calibrated_confidence")
        assert hasattr(result, "entropy_ratio")
        assert hasattr(result, "margin")
        assert hasattr(result, "needs_human_review")
        assert result.calibrated is True
        assert result.calibrated_confidence > 0
        assert 0 <= result.entropy_ratio <= 1


# ==================== INNOVATION 3: SEMANTIC CHUNKING ====================

class TestSemanticChunking:
    """Test semantic chunking."""

    def test_chunks_well_structured_contract(self):
        from src.v10.semantic_chunker import SemanticChunker

        contract = """
1. DEFINITIONS
In this Agreement, the following terms shall have the meanings set forth below.
"Confidential Information" means any information marked as confidential.
"Services" means the consulting services described in Exhibit A.

2. SCOPE OF SERVICES
Provider shall perform the Services as described in each Statement of Work.
Any changes to scope require a written change order signed by both parties.

3. PAYMENT TERMS
Client shall pay all invoices within thirty days of receipt.
Late payments accrue interest at 1.5% per month.

4. CONFIDENTIALITY
Each party agrees to maintain confidentiality of information received.
This obligation survives for three years after termination.

5. TERMINATION
Either party may terminate this Agreement for cause upon thirty days notice.
Either party may terminate for convenience upon sixty days notice.
"""
        chunker = SemanticChunker()
        chunks = chunker.chunk(contract)
        assert len(chunks) >= 3, f"Expected >= 3 chunks, got {len(chunks)}"
        for chunk in chunks:
            assert len(chunk.text) > 20

    def test_handles_short_text(self):
        from src.v10.semantic_chunker import SemanticChunker

        chunker = SemanticChunker()
        chunks = chunker.chunk("This is a very short text.")
        assert isinstance(chunks, list)

    def test_chunks_have_required_fields(self):
        from src.v10.semantic_chunker import SemanticChunker, SemanticChunk

        chunker = SemanticChunker()
        chunks = chunker.chunk(
            "1. FIRST SECTION\nThis is the first section with enough content.\n\n"
            "2. SECOND SECTION\nThis is the second section with different content.\n\n"
            "3. THIRD SECTION\nThis is the third section about termination.\n\n"
            "4. FOURTH SECTION\nThis is the fourth section about payment."
        )
        for chunk in chunks:
            assert isinstance(chunk, SemanticChunk)
            assert hasattr(chunk, "id")
            assert hasattr(chunk, "text")
            assert hasattr(chunk, "header")
            assert hasattr(chunk, "coherence_score")


# ==================== INNOVATION 4: RISK SIMULATION ====================

class TestRiskSimulation:
    """Test Monte Carlo risk simulation."""

    def test_simulation_produces_valid_distribution(self):
        from src.v10.risk_simulator import RiskSimulator

        sim = RiskSimulator(n_simulations=500, seed=42)
        result = sim.simulate(
            classified_clauses=[
                {"confidence": 0.8, "top_3": [("indemnification", 0.8), ("warranty", 0.4)]},
                {"confidence": 0.6, "top_3": [("termination", 0.6), ("payment_terms", 0.55)]},
            ],
            graph_analysis_dict={
                "structural_risk": 45,
                "completeness_score": 0.7,
                "conflict_count": 2,
                "dependency_gap_count": 1,
            },
            power_analysis_dict={
                "power_score": 35,
                "total_obligations": 10,
                "total_protections": 8,
            },
            dispute_analysis_dict={
                "overall_dispute_risk": 55,
            },
            base_risk_score=50.0,
        )

        assert result.n_simulations == 500
        assert 0 <= result.mean_risk <= 100
        assert result.ci_95_lower <= result.mean_risk <= result.ci_95_upper
        assert result.best_case_risk <= result.worst_case_risk
        assert result.risk_volatility in ("low", "medium", "high")
        assert len(result.histogram_counts) == 10

    def test_high_uncertainty_produces_wide_ci(self):
        from src.v10.risk_simulator import RiskSimulator

        sim = RiskSimulator(n_simulations=500, seed=42)
        # Low confidence = ambiguous classifications
        result = sim.simulate(
            classified_clauses=[
                {"confidence": 0.35, "top_3": [("indemnification", 0.35), ("warranty", 0.34)]},
                {"confidence": 0.36, "top_3": [("termination", 0.36), ("payment_terms", 0.35)]},
            ],
            graph_analysis_dict={"structural_risk": 50, "completeness_score": 0.3, "conflict_count": 5, "dependency_gap_count": 3},
            power_analysis_dict={"power_score": 50, "total_obligations": 2, "total_protections": 2},
            dispute_analysis_dict={"overall_dispute_risk": 50},
            base_risk_score=50.0,
        )
        ci_width = result.ci_95_upper - result.ci_95_lower
        assert ci_width > 10, f"Expected wide CI for uncertain inputs, got {ci_width}"


# ==================== INNOVATION 5: CORPUS INTELLIGENCE ====================

class TestCorpusIntelligence:
    """Test cross-contract corpus learning."""

    def test_ingest_and_compare(self):
        import tempfile
        from src.v10.corpus_intelligence import CorpusIntelligence

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            profile_path = f.name

        try:
            ci = CorpusIntelligence(profile_path=profile_path)

            # Ingest 5 mock reports
            for i in range(5):
                mock_report = {
                    "metadata": {"contract_type": "MSA", "total_clauses": 10 + i},
                    "classifications": [
                        {"clause_type": "indemnification", "confidence": 0.75 + i * 0.02, "risk_weight": 0.8, "text_preview": "x" * 100, "id": "1"},
                        {"clause_type": "termination", "confidence": 0.7 + i * 0.01, "risk_weight": 0.6, "text_preview": "x" * 80, "id": "2"},
                        {"clause_type": "confidentiality", "confidence": 0.8, "risk_weight": 0.5, "text_preview": "x" * 90, "id": "3"},
                    ],
                    "overall": {"risk_score": 45 + i * 3},
                }
                ci.ingest(mock_report)

            assert ci.profile.total_contracts == 5

            # Compare a new contract
            new_report = {
                "metadata": {"contract_type": "MSA", "total_clauses": 8},
                "classifications": [
                    {"clause_type": "indemnification", "confidence": 0.4, "risk_weight": 0.8, "text_preview": "x" * 50, "id": "1"},
                ],
                "overall": {"risk_score": 85},
            }
            comparison = ci.compare(new_report)
            assert comparison.risk_z_score > 1.0, "High risk contract should have positive z-score"
            assert len(comparison.anomalies) > 0
        finally:
            os.unlink(profile_path)

    def test_persistence(self):
        import tempfile
        from src.v10.corpus_intelligence import CorpusIntelligence

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            profile_path = f.name

        try:
            # Create and populate
            ci1 = CorpusIntelligence(profile_path=profile_path)
            for i in range(3):
                ci1.ingest({
                    "metadata": {"contract_type": "NDA", "total_clauses": 5},
                    "classifications": [{"clause_type": "confidentiality", "confidence": 0.9, "risk_weight": 0.5, "text_preview": "x", "id": "1"}],
                    "overall": {"risk_score": 30},
                })

            # Reload from disk
            ci2 = CorpusIntelligence(profile_path=profile_path)
            assert ci2.profile.total_contracts == 3
        finally:
            os.unlink(profile_path)


# ==================== INTEGRATION TEST ====================

class TestV11Pipeline:
    """Integration test for the full V11 pipeline."""

    def test_full_pipeline_with_all_innovations(self):
        """Run the complete pipeline with all V11 features enabled."""
        from src.v10.pipeline import V10Pipeline

        contract = """
1. INDEMNIFICATION
Provider shall indemnify, defend, and hold harmless the Client from any claims,
losses, damages, and expenses arising from Provider's breach of this Agreement.

2. LIMITATION OF LIABILITY
Provider's total aggregate liability shall not exceed the fees paid in the
preceding twelve months. Neither party shall be liable for indirect damages.

3. TERMINATION
Either party may terminate for material breach upon thirty days written notice.
Termination for convenience requires sixty days prior written notice.

4. CONFIDENTIALITY
Both parties agree to maintain the confidentiality of proprietary information.
This obligation survives for three years after termination.

5. GOVERNING LAW
This Agreement shall be governed by the laws of France.
Disputes shall be submitted to the courts of Paris.

6. PAYMENT TERMS
All invoices are due within thirty days of receipt.
Late payments accrue interest at the rate of 1.5% per month.
"""
        pipeline = V10Pipeline(multilingual=True)
        report = pipeline.analyze(
            contract_text=contract,
            contract_type="MSA",
            suggest_rewrites=True,
            simulate_risk=True,
            corpus_compare=True,
            use_semantic_chunking=True,
        )

        # Core V10 assertions
        assert report.total_clauses >= 3
        assert report.risk_level in ("LOW", "MEDIUM", "HIGH")
        assert 0 <= report.overall_risk_score <= 100
        assert report.engine_version == "V11"

        # V11 assertions
        report_dict = report.to_dict()

        # Calibrated classification
        for c in report_dict["classifications"]:
            assert "calibrated_confidence" in c
            assert "entropy_ratio" in c
            assert "margin" in c
            assert "needs_human_review" in c

        # Risk simulation should be present
        if report.risk_simulation:
            sim = report.risk_simulation
            assert "mean_risk" in sim
            assert "confidence_interval_95" in sim
            assert "risk_volatility" in sim
            assert sim["confidence_interval_95"][0] <= sim["mean_risk"]

        # Report should serialize to JSON
        json_output = report.to_json()
        assert len(json_output) > 100

        print(f"\n V11 Pipeline Test Passed!")
        print(f"   Clauses: {report.total_clauses}")
        print(f"   Risk: {report.overall_risk_score:.1f} ({report.risk_level})")
        print(f"   Time: {report.analysis_time_ms}ms")
        print(f"   Engine: {report.engine_version}")
        if report.risk_simulation:
            sim = report.risk_simulation
            print(f"   Risk CI95: [{sim['confidence_interval_95'][0]}, {sim['confidence_interval_95'][1]}]")
            print(f"   Risk Volatility: {sim['risk_volatility']}")
        if report.suggested_rewrites:
            print(f"   Rewrite Suggestions: {len(report.suggested_rewrites)}")
        if report.corpus_comparison:
            print(f"   Corpus Comparison: {report.corpus_comparison.get('summary', 'N/A')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
