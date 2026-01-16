"""
BALE Core Graph
Main workflow compilation with multi-jurisdiction support.
"""
from langgraph.graph import StateGraph, END
from src.types import BaleState
from src.agents import BaleAgents
from src.logger import setup_logger

logger = setup_logger("bale_graph")


def compile_graph(enhanced: bool = True):
    """
    Compile the BALE analysis graph.
    
    Args:
        enhanced: If True, use multi-jurisdiction enhanced graph.
                 If False, use basic sequential graph.
    
    Returns:
        Compiled LangGraph application.
    """
    if enhanced:
        try:
            from src.graph_enhanced import compile_enhanced_graph
            logger.info("Compiling enhanced multi-jurisdiction graph")
            return compile_enhanced_graph()
        except ImportError as e:
            logger.warning(f"Enhanced graph unavailable: {e}, falling back to basic")
    
    return compile_basic_graph()


def compile_basic_graph():
    """Compile the basic sequential analysis graph."""
    agents = BaleAgents()
    
    workflow = StateGraph(BaleState)

    # Add Nodes
    workflow.add_node("civilist", agents.civilist_node)
    workflow.add_node("commonist", agents.commonist_node)
    workflow.add_node("ip_specialist", agents.ip_specialist_node)
    workflow.add_node("synthesizer", agents.synthesizer_node)
    workflow.add_node("simulation", agents.simulation_node)
    workflow.add_node("harmonizer", agents.harmonizer_node)
    workflow.add_node("gatekeeper", agents.gatekeeper_node)

    # Define entry point
    workflow.set_entry_point("civilist")

    # Sequential flow
    workflow.add_edge("civilist", "commonist")
    workflow.add_edge("commonist", "ip_specialist")
    workflow.add_edge("ip_specialist", "synthesizer")
    workflow.add_edge("synthesizer", "simulation")
    workflow.add_edge("simulation", "harmonizer")
    workflow.add_edge("harmonizer", "gatekeeper")
    workflow.add_edge("gatekeeper", END)

    app = workflow.compile()
    logger.info("Compiled basic sequential graph")
    return app


def compile_quick_graph():
    """Compile a minimal graph for quick analysis."""
    try:
        from src.graph_enhanced import compile_quick_graph as enhanced_quick
        return enhanced_quick()
    except ImportError:
        # Fallback to basic
        return compile_basic_graph()


# Convenience exports
def get_default_graph():
    """Get the default production graph."""
    return compile_graph(enhanced=True)


if __name__ == "__main__":
    app = compile_graph()
    test_state = {
        "content": "Test contract text regarding Force Majeure...",
        "jurisdiction": "UK",
        "execution_mode": "local"
    }
    output = app.invoke(test_state)
    print(output)

