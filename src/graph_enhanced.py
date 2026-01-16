"""
BALE Enhanced Workflow Graph
Multi-jurisdiction aware pipeline with dynamic agent routing.
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any, List

from src.types import BaleState
from src.agents import BaleAgents
from src.multi_jurisdiction_agents import MultiJurisdictionAgents
from src.jurisdiction import (
    JurisdictionDetector, Jurisdiction, LegalFamily,
    JURISDICTION_PROFILES, detect_jurisdiction
)
from src.logger import setup_logger

logger = setup_logger("bale_enhanced_graph")


def compile_enhanced_graph(
    jurisdictions: List[Jurisdiction] = None,
    include_cross_border: bool = True
):
    """
    Compile an enhanced BALE graph with multi-jurisdiction support.
    
    Args:
        jurisdictions: Specific jurisdictions to analyze (auto-detect if None)
        include_cross_border: Whether to include cross-border conflict analysis
    
    Returns:
        Compiled LangGraph workflow
    """
    agents = BaleAgents()
    multi_agents = MultiJurisdictionAgents(agents)
    detector = JurisdictionDetector()
    
    workflow = StateGraph(BaleState)
    
    # ==================== NODE DEFINITIONS ====================
    
    def jurisdiction_detector_node(state: BaleState) -> Dict:
        """Detect applicable jurisdiction(s) from content."""
        content = state.get("content", "")
        explicit_jurisdiction = state.get("jurisdiction")
        
        if explicit_jurisdiction:
            # User specified jurisdiction
            try:
                j = Jurisdiction(explicit_jurisdiction)
                return {
                    "detected_jurisdiction": j.value,
                    "jurisdiction_confidence": 1.0,
                    "jurisdiction_metadata": {"explicit": True}
                }
            except:
                pass
        
        # Auto-detect
        j, confidence, metadata = detector.detect(content)
        
        return {
            "detected_jurisdiction": j.value,
            "jurisdiction_confidence": confidence,
            "jurisdiction_metadata": metadata
        }
    
    def route_by_jurisdiction(state: BaleState) -> str:
        """Route to appropriate analysis path based on jurisdiction."""
        j_str = state.get("detected_jurisdiction", "INTERNATIONAL")
        
        try:
            j = Jurisdiction(j_str)
        except:
            j = Jurisdiction.INTERNATIONAL
        
        profile = JURISDICTION_PROFILES.get(j)
        if not profile:
            return "standard_path"
        
        if profile.legal_family == LegalFamily.CIVIL_LAW:
            if j == Jurisdiction.GERMANY:
                return "german_path"
            return "civil_path"
        elif profile.legal_family == LegalFamily.COMMON_LAW:
            if j == Jurisdiction.US:
                return "us_path"
            return "common_path"
        elif profile.legal_family == LegalFamily.EU_LAW:
            return "eu_path"
        else:
            return "international_path"
    
    def merge_opinions_node(state: BaleState) -> Dict:
        """Merge all jurisdiction opinions for synthesis."""
        opinions = []
        
        if state.get("civilist_opinion"):
            opinions.append(("CIVIL_LAW", state["civilist_opinion"]))
        if state.get("commonist_opinion"):
            opinions.append(("COMMON_LAW", state["commonist_opinion"]))
        if state.get("us_commercial_opinion"):
            opinions.append(("US_LAW", state["us_commercial_opinion"]))
        if state.get("germanist_opinion"):
            opinions.append(("GERMAN_LAW", state["germanist_opinion"]))
        if state.get("eu_law_opinion"):
            opinions.append(("EU_LAW", state["eu_law_opinion"]))
        
        return {"all_opinions": opinions}
    
    # ==================== ADD NODES ====================
    
    # Detection
    workflow.add_node("detect_jurisdiction", jurisdiction_detector_node)
    
    # Core agents (from base)
    workflow.add_node("civilist", agents.civilist_node)
    workflow.add_node("commonist", agents.commonist_node)
    workflow.add_node("ip_specialist", agents.ip_specialist_node)
    
    # Multi-jurisdiction agents
    workflow.add_node("us_commercial", multi_agents.us_commercial_node)
    workflow.add_node("germanist", multi_agents.germanist_node)
    workflow.add_node("eu_law", multi_agents.eu_law_node)
    workflow.add_node("cross_border", multi_agents.cross_border_node)
    
    # Core pipeline
    workflow.add_node("merge_opinions", merge_opinions_node)
    workflow.add_node("synthesizer", agents.synthesizer_node)
    workflow.add_node("simulation", agents.simulation_node)
    workflow.add_node("harmonizer", agents.harmonizer_node)
    workflow.add_node("gatekeeper", agents.gatekeeper_node)
    
    # ==================== DEFINE FLOW ====================
    
    workflow.set_entry_point("detect_jurisdiction")
    
    # Conditional routing based on jurisdiction
    workflow.add_conditional_edges(
        "detect_jurisdiction",
        route_by_jurisdiction,
        {
            "civil_path": "civilist",
            "common_path": "commonist",
            "us_path": "us_commercial",
            "german_path": "germanist",
            "eu_path": "eu_law",
            "international_path": "civilist",
            "standard_path": "civilist"
        }
    )
    
    # Civil Law path
    workflow.add_edge("civilist", "commonist")
    
    # Common Law path
    workflow.add_edge("commonist", "ip_specialist")
    
    # US path (joins common law)
    workflow.add_edge("us_commercial", "commonist")
    
    # German path (joins civil law)
    workflow.add_edge("germanist", "civilist")
    
    # EU path (analyzes both)
    workflow.add_edge("eu_law", "civilist")
    
    # IP specialist to merge
    workflow.add_edge("ip_specialist", "merge_opinions")
    
    # Cross-border analysis if multiple jurisdictions
    if include_cross_border:
        workflow.add_edge("merge_opinions", "cross_border")
        workflow.add_edge("cross_border", "synthesizer")
    else:
        workflow.add_edge("merge_opinions", "synthesizer")
    
    # Standard pipeline end
    workflow.add_edge("synthesizer", "simulation")
    workflow.add_edge("simulation", "harmonizer")
    workflow.add_edge("harmonizer", "gatekeeper")
    workflow.add_edge("gatekeeper", END)
    
    return workflow.compile()


def compile_graph():
    """
    Enhanced version of compile_graph for backwards compatibility.
    Returns the new multi-jurisdiction aware graph.
    """
    return compile_enhanced_graph(include_cross_border=True)


# ==================== QUICK ANALYSIS PATHS ====================

def compile_quick_graph():
    """
    Compile a faster graph for quick analysis.
    Skips some agents for speed.
    """
    agents = BaleAgents()
    workflow = StateGraph(BaleState)
    
    workflow.add_node("civilist", agents.civilist_node)
    workflow.add_node("commonist", agents.commonist_node)
    workflow.add_node("synthesizer", agents.synthesizer_node)
    workflow.add_node("gatekeeper", agents.gatekeeper_node)
    
    workflow.set_entry_point("civilist")
    workflow.add_edge("civilist", "commonist")
    workflow.add_edge("commonist", "synthesizer")
    workflow.add_edge("synthesizer", "gatekeeper")
    workflow.add_edge("gatekeeper", END)
    
    return workflow.compile()


def compile_deep_graph():
    """
    Compile the full deep analysis graph with all agents.
    """
    return compile_enhanced_graph(include_cross_border=True)


if __name__ == "__main__":
    # Test the enhanced graph
    app = compile_enhanced_graph()
    test_state = {
        "content": """
        This Agreement shall be governed by and construed in accordance with 
        the laws of England and Wales. The Supplier shall not be liable for 
        any indirect, consequential, or incidental damages under Article 82 GDPR 
        or otherwise arising from this Agreement.
        """,
        "execution_mode": "local"
    }
    
    print("Testing enhanced graph with UK/EU content...")
    # output = app.invoke(test_state)
    # print(output)
