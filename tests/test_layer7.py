import os
import json
import pytest
from common.config import OUTPUT_DIR
from layer1_instrumentation.mock_controller import MockDeviceController
from layer3_agent.explorer import ExplorationAgent
from layer4_understanding.vlm_client import VlmScreenAnalyzer
from layer5_design.design_system import extract_design_system
from layer6_graph.graph_builder import JourneyGraphBuilder
from layer7_compiler.compiler import KnowledgePackCompiler, AppKnowledgePack

def test_knowledge_pack_compilation_and_size_ceiling():
    controller = MockDeviceController()
    agent = ExplorationAgent(controller=controller, step_budget=20)
    screens, transitions = agent.explore()
    
    analyzer = VlmScreenAnalyzer(provider="offline_heuristic")
    understandings = {fp: analyzer.analyze_screen(s) for fp, s in screens.items()}
    
    design_system = extract_design_system(list(screens.values()))
    builder = JourneyGraphBuilder()
    graph = builder.build_graph(screens, understandings, transitions)
    
    compiler = KnowledgePackCompiler()
    out_file = str(OUTPUT_DIR / "test_knowledge_pack.json")
    pack = compiler.compile(
        package_name="com.revrag.sampleapp",
        screens=screens,
        screen_understandings=understandings,
        design_system=design_system,
        screen_graph=graph,
        output_file_path=out_file
    )
    
    assert isinstance(pack, AppKnowledgePack)
    assert pack.metadata.total_screens_discovered >= 3
    # Check size constraint: MUST be well below 1.5MB (1500 KB)
    assert pack.metadata.pack_size_kb < 1500
    # Usually it is < 50 KB
    assert pack.metadata.pack_size_kb < 100
    
    # Verify file was written and is valid JSON
    assert os.path.exists(out_file)
    with open(out_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
        assert loaded["metadata"]["package_name"] == "com.revrag.sampleapp"
        assert len(loaded["screen_profiles"]) >= 3
