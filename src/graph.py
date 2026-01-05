from langgraph.graph import StateGraph, END
from src.types import BaleState
from src.agents import BaleAgents

def compile_graph():
    agents = BaleAgents()
    
    workflow = StateGraph(BaleState)

    # Add Nodes
    workflow.add_node("civilist", agents.civilist_node)
    workflow.add_node("commonist", agents.commonist_node)
    workflow.add_node("synthesizer", agents.synthesizer_node)
    workflow.add_node("simulation", agents.simulation_node)
    workflow.add_node("harmonizer", agents.harmonizer_node)
    workflow.add_node("gatekeeper", agents.gatekeeper_node)

    # Define API
    workflow.set_entry_point("civilist")

    # Sequential Loop
    workflow.add_edge("civilist", "commonist")
    workflow.add_edge("commonist", "synthesizer")
    workflow.add_edge("synthesizer", "simulation")
    workflow.add_edge("simulation", "harmonizer")
    workflow.add_edge("harmonizer", "gatekeeper")
    workflow.add_edge("gatekeeper", END)

    app = workflow.compile()
    return app

if __name__ == "__main__":
    app = compile_graph()
    test_state = {"content": "Test contract text regarding Force Majeure..."}
    output = app.invoke(test_state)
    print(output)
