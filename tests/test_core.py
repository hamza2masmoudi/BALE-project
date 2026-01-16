"""
BALE Core Module Tests
Unit tests for adjudication, ontology, and explainability.
"""
import pytest
from datetime import datetime

# ==================== ADJUDICATION TESTS ====================

class TestDecisionFactors:
    """Test the DecisionFactors model and calculate_litigation_risk."""
    
    def test_import_adjudication(self):
        """Test adjudication module imports."""
        from src.adjudication import DecisionFactors, calculate_litigation_risk
        assert DecisionFactors is not None
        assert calculate_litigation_risk is not None
    
    def test_high_risk_scenario(self):
        """Ambiguous + mandatory law + plausible = high risk."""
        from src.adjudication import DecisionFactors, calculate_litigation_risk
        
        factors = DecisionFactors(
            is_ambiguous=True,
            is_exclusion_clear=False,
            authority_is_mandatory=True,
            plaintiff_plausible=True
        )
        
        risk, verdict = calculate_litigation_risk(factors)
        
        assert risk >= 70, f"Expected high risk, got {risk}"
        assert verdict == "PLAINTIFF_FAVOR"
    
    def test_low_risk_scenario(self):
        """Clear + no mandatory + implausible = low risk."""
        from src.adjudication import DecisionFactors, calculate_litigation_risk
        
        factors = DecisionFactors(
            is_ambiguous=False,
            is_exclusion_clear=True,
            authority_is_mandatory=False,
            plaintiff_plausible=False
        )
        
        risk, verdict = calculate_litigation_risk(factors)
        
        assert risk <= 40, f"Expected low risk, got {risk}"
        assert verdict == "DEFENSE_FAVOR"
    
    def test_medium_risk_scenario(self):
        """Mixed factors = medium risk."""
        from src.adjudication import DecisionFactors, calculate_litigation_risk
        
        factors = DecisionFactors(
            is_ambiguous=True,
            is_exclusion_clear=True,
            authority_is_mandatory=False,
            plaintiff_plausible=True
        )
        
        risk, verdict = calculate_litigation_risk(factors)
        
        assert 30 <= risk <= 70, f"Expected medium risk, got {risk}"
    
    def test_risk_bounds(self):
        """Risk should always be between 0 and 100."""
        from src.adjudication import DecisionFactors, calculate_litigation_risk
        
        for is_amb in [True, False]:
            for is_excl in [True, False]:
                for is_mand in [True, False]:
                    for is_plaus in [True, False]:
                        factors = DecisionFactors(
                            is_ambiguous=is_amb,
                            is_exclusion_clear=is_excl,
                            authority_is_mandatory=is_mand,
                            plaintiff_plausible=is_plaus
                        )
                        risk, _ = calculate_litigation_risk(factors)
                        assert 0 <= risk <= 100


# ==================== ONTOLOGY TESTS ====================

class TestLegalOntology:
    """Test the legal ontology models."""
    
    def test_legal_system_enum(self):
        """Test LegalSystem enum values."""
        from src.ontology import LegalSystem
        
        assert LegalSystem.CIVIL_LAW.value == "CIVIL_LAW"
        assert LegalSystem.COMMON_LAW.value == "COMMON_LAW"
    
    def test_authority_level_weights(self):
        """Test authority level weights hierarchy."""
        from src.ontology import AuthorityLevel
        
        assert AuthorityLevel.CONSTITUTIONAL.weight > AuthorityLevel.STATUTORY.weight
        assert AuthorityLevel.STATUTORY.weight > AuthorityLevel.SUPREME_COURT.weight
        assert AuthorityLevel.SUPREME_COURT.weight > AuthorityLevel.CONTRACTUAL.weight
    
    def test_legal_node_creation(self):
        """Test LegalNode creation and weight calculation."""
        from src.ontology import LegalNode, LegalSystem, AuthorityLevel, BindingStatus
        
        node = LegalNode(
            id="test_1",
            text_content="Test legal content",
            system=LegalSystem.CIVIL_LAW,
            authority_level=AuthorityLevel.STATUTORY,
            binding_status=BindingStatus.MANDATORY
        )
        
        assert node.id == "test_1"
        assert node.system == LegalSystem.CIVIL_LAW
        
        weight = node.calculate_weight()
        assert weight > 0


# ==================== EXPLAINABILITY TESTS ====================

class TestExplainability:
    """Test the explainability module."""
    
    def test_explainability_import(self):
        """Test explainability module imports."""
        from src.explainability import (
            ExplainabilityEngine,
            ExplainableVerdict,
            DecisionFactor,
            CounterfactualScenario
        )
        assert ExplainabilityEngine is not None
    
    def test_decision_factor_creation(self):
        """Test DecisionFactor dataclass."""
        from src.explainability import DecisionFactor
        
        factor = DecisionFactor(
            rule_name="Contra Proferentem",
            rule_description="Ambiguous terms interpreted against drafter",
            triggered=True,
            impact_on_risk=15,
            evidence="Clause uses undefined term 'reasonable'"
        )
        
        assert factor.triggered is True
        assert factor.impact_on_risk == 15
    
    def test_explainable_verdict_structure(self):
        """Test ExplainableVerdict has required fields."""
        from src.explainability import ExplainableVerdict, DecisionFactor
        
        verdict = ExplainableVerdict(
            risk_score=65,
            verdict="PLAINTIFF_FAVOR",
            confidence=0.85,
            decision_factors=[
                DecisionFactor(
                    rule_name="Test Rule",
                    rule_description="Test description",
                    triggered=True,
                    impact_on_risk=10,
                    evidence="Test evidence"
                )
            ],
            interpretive_gap=25,
            civilist_summary="Civil law analysis...",
            commonist_summary="Common law analysis...",
            synthesis="Combined analysis...",
            citations=[],
            counterfactuals=[]
        )
        
        assert verdict.risk_score == 65
        assert len(verdict.decision_factors) == 1


# ==================== JURISDICTION TESTS ====================

class TestJurisdiction:
    """Test jurisdiction detection."""
    
    def test_detect_uk_jurisdiction(self):
        """Test UK jurisdiction detection."""
        from src.jurisdiction import detect_jurisdiction, Jurisdiction
        
        text = "This Agreement shall be governed by the laws of England and Wales."
        j, confidence, _ = detect_jurisdiction(text)
        
        assert j == Jurisdiction.UK
        assert confidence > 0.7
    
    def test_detect_france_jurisdiction(self):
        """Test French jurisdiction detection."""
        from src.jurisdiction import detect_jurisdiction, Jurisdiction
        
        text = "Le présent contrat est régi par le droit français, Article 1104 du Code Civil."
        j, confidence, _ = detect_jurisdiction(text)
        
        assert j == Jurisdiction.FRANCE
        assert confidence > 0.5
    
    def test_detect_us_jurisdiction(self):
        """Test US jurisdiction detection."""
        from src.jurisdiction import detect_jurisdiction, Jurisdiction
        
        text = "This Agreement is governed by the laws of the State of Delaware and the UCC."
        j, confidence, _ = detect_jurisdiction(text)
        
        assert j == Jurisdiction.US
        assert confidence > 0.7
    
    def test_jurisdiction_profiles(self):
        """Test jurisdiction profiles are complete."""
        from src.jurisdiction import JURISDICTION_PROFILES, Jurisdiction
        
        for j in Jurisdiction:
            profile = JURISDICTION_PROFILES.get(j)
            assert profile is not None, f"Missing profile for {j}"
            assert profile.key_statutes, f"No statutes for {j}"


# ==================== KNOWLEDGE GRAPH TESTS ====================

class TestKnowledgeGraph:
    """Test knowledge graph models (without Neo4j connection)."""
    
    def test_node_creation(self):
        """Test LegalGraphNode creation."""
        from src.knowledge_graph import LegalGraphNode, NodeType, Jurisdiction
        
        node = LegalGraphNode(
            id="test_node",
            node_type=NodeType.STATUTE,
            name="Test Statute",
            jurisdiction=Jurisdiction.UK,
            authority_level=90
        )
        
        assert node.id == "test_node"
        assert node.node_type == NodeType.STATUTE
    
    def test_relation_types(self):
        """Test relation type enum."""
        from src.knowledge_graph import RelationType
        
        assert RelationType.CITES.value == "CITES"
        assert RelationType.OVERRULES.value == "OVERRULES"
        assert RelationType.EQUIVALENT_TO.value == "EQUIVALENT_TO"
    
    def test_client_initialization(self):
        """Test client can be created without connection."""
        from src.knowledge_graph import KnowledgeGraphClient
        
        client = KnowledgeGraphClient(uri="bolt://localhost:7687")
        assert client is not None
        assert client.is_connected is False  # Not connected yet


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
