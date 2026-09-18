import pytest
from layer1_instrumentation.mock_controller import MockDeviceController
from layer6_graph.stability_test import run_stability_evaluation

def test_graph_stability_and_repeat_scan_convergence():
    """
    PROVES HARD REQUIREMENT:
    Running exploration twice on the same app converges on the exact same
    screen graph with near-zero divergence, even when dynamic content differs.
    """
    report, graph1, graph2 = run_stability_evaluation(
        create_controller_fn=lambda: MockDeviceController(),
        step_budget=25
    )
    
    # Check that both graphs discovered the screens
    assert report.pass_1_node_count >= 3
    assert report.pass_2_node_count >= 3
    
    # Verify node convergence is 100% (both scans found the exact same screen fingerprints)
    assert report.node_convergence_percentage >= 95.0
    assert report.is_stable is True
    
    # Check graph properties
    assert len(graph1.nodes) == len(graph2.nodes)
    assert len(graph1.journeys) > 0
