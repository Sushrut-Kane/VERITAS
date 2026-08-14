"""LangGraph StateGraph definition and compiled pipeline.

Linear graph — no branching/looping for the MVP. Retries live on individual LLM
calls (tenacity), keeping the graph structure simple to reason about.

    extract_claims -> normalize_units -> write_to_graph -> cross_document_check
      -> red_team_attack -> classify -> policy_decide -> persist
"""
from langgraph.graph import END, START, StateGraph

from app.agents.nodes.classify import classify
from app.agents.nodes.cross_document_check import cross_document_check
from app.agents.nodes.extract_claims import extract_claims
from app.agents.nodes.normalize_units import normalize_units
from app.agents.nodes.persist import persist
from app.agents.nodes.policy_decide import policy_decide
from app.agents.nodes.red_team import red_team_attack
from app.agents.nodes.write_to_graph import write_to_graph
from app.schemas.pipeline_state import PipelineState


def build_pipeline():
    graph = StateGraph(PipelineState)

    graph.add_node("extract_claims", extract_claims)
    graph.add_node("normalize_units", normalize_units)
    graph.add_node("write_to_graph", write_to_graph)
    graph.add_node("cross_document_check", cross_document_check)
    graph.add_node("red_team_attack", red_team_attack)
    graph.add_node("classify", classify)
    graph.add_node("policy_decide", policy_decide)
    graph.add_node("persist", persist)

    graph.add_edge(START, "extract_claims")
    graph.add_edge("extract_claims", "normalize_units")
    graph.add_edge("normalize_units", "write_to_graph")
    graph.add_edge("write_to_graph", "cross_document_check")
    graph.add_edge("cross_document_check", "red_team_attack")
    graph.add_edge("red_team_attack", "classify")
    graph.add_edge("classify", "policy_decide")
    graph.add_edge("policy_decide", "persist")
    graph.add_edge("persist", END)

    return graph.compile()


pipeline = build_pipeline()
