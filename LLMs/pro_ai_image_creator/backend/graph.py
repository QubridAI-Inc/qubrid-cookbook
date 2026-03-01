from langgraph.graph import StateGraph, END
from backend.state import AgentState
from backend.nodes import generate_asset_node

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("generate_asset", generate_asset_node)
    workflow.set_entry_point("generate_asset")
    workflow.add_edge("generate_asset", END)
    return workflow.compile()