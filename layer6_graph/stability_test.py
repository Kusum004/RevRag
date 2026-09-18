from typing import Dict, Any, Tuple
from pydantic import BaseModel
from common.models import ScreenState, TransitionEdge
from layer1_instrumentation.base import IDeviceController
from layer3_agent.explorer import ExplorationAgent
from layer4_understanding.vlm_client import VlmScreenAnalyzer
from layer6_graph.graph_builder import JourneyGraphBuilder, AppJourneyGraph

class StabilityDiffReport(BaseModel):
    pass_1_node_count: int
    pass_2_node_count: int
    common_nodes_count: int
    node_convergence_percentage: float
    pass_1_edge_count: int
    pass_2_edge_count: int
    common_edges_count: int
    edge_convergence_percentage: float
    is_stable: bool

def run_stability_evaluation(
    create_controller_fn,
    step_budget: int = 25
) -> Tuple[StabilityDiffReport, AppJourneyGraph, AppJourneyGraph]:
    """
    Executes two independent exploration cycles on the same target app
    and computes the structural graph convergence diff.
    """
    analyzer = VlmScreenAnalyzer(provider="offline_heuristic")
    builder = JourneyGraphBuilder()

    # Pass 1
    ctrl1 = create_controller_fn()
    agent1 = ExplorationAgent(controller=ctrl1, step_budget=step_budget)
    screens1, trans1 = agent1.explore()
    und1 = {fp: analyzer.analyze_screen(s) for fp, s in screens1.items()}
    graph1 = builder.build_graph(screens1, und1, trans1)

    # Pass 2 (Independent run, possibly with dynamic content variation)
    ctrl2 = create_controller_fn()
    if hasattr(ctrl2, "set_dynamic_variation"):
        ctrl2.set_dynamic_variation(1)  # Simulates dynamic content differences!
    agent2 = ExplorationAgent(controller=ctrl2, step_budget=step_budget)
    screens2, trans2 = agent2.explore()
    und2 = {fp: analyzer.analyze_screen(s) for fp, s in screens2.items()}
    graph2 = builder.build_graph(screens2, und2, trans2)

    # Compare Nodes
    nodes1 = {n.fingerprint for n in graph1.nodes}
    nodes2 = {n.fingerprint for n in graph2.nodes}
    common_nodes = nodes1.intersection(nodes2)
    total_nodes = nodes1.union(nodes2)
    node_conv = (len(common_nodes) / len(total_nodes) * 100.0) if total_nodes else 100.0

    # Compare Edges
    edges1 = {(e.from_fingerprint, e.to_fingerprint, e.action_type) for e in graph1.edges}
    edges2 = {(e.from_fingerprint, e.to_fingerprint, e.action_type) for e in graph2.edges}
    common_edges = edges1.intersection(edges2)
    total_edges = edges1.union(edges2)
    edge_conv = (len(common_edges) / len(total_edges) * 100.0) if total_edges else 100.0

    report = StabilityDiffReport(
        pass_1_node_count=len(nodes1),
        pass_2_node_count=len(nodes2),
        common_nodes_count=len(common_nodes),
        node_convergence_percentage=round(node_conv, 2),
        pass_1_edge_count=len(edges1),
        pass_2_edge_count=len(edges2),
        common_edges_count=len(common_edges),
        edge_convergence_percentage=round(edge_conv, 2),
        is_stable=node_conv >= 90.0
    )

    return report, graph1, graph2
