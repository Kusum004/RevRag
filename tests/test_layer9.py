import os
import pytest
from common.config import OUTPUT_DIR
from layer1_instrumentation.mock_controller import MockDeviceController
from layer3_agent.explorer import ExplorationAgent
from layer4_understanding.vlm_client import VlmScreenAnalyzer
from layer5_design.design_system import extract_design_system
from layer6_graph.graph_builder import JourneyGraphBuilder
from layer7_compiler.compiler import KnowledgePackCompiler
from layer9_rebuild.rebuilder import ScreenRebuilder
from layer9_rebuild.comparator import generate_side_by_side_fidelity_proof

def test_screen_rebuild_from_knowledge_pack_alone():
    controller = MockDeviceController()
    agent = ExplorationAgent(controller=controller, step_budget=20)
    screens, transitions = agent.explore()
    
    analyzer = VlmScreenAnalyzer(provider="offline_heuristic")
    understandings = {fp: analyzer.analyze_screen(s) for fp, s in screens.items()}
    design_system = extract_design_system(list(screens.values()))
    builder = JourneyGraphBuilder()
    graph = builder.build_graph(screens, understandings, transitions)
    
    compiler = KnowledgePackCompiler()
    pack = compiler.compile(
        package_name="com.revrag.sampleapp",
        screens=screens,
        screen_understandings=understandings,
        design_system=design_system,
        screen_graph=graph
    )
    
    rebuilder = ScreenRebuilder(pack)
    
    # Rebuild 2-3 screens
    fingerprints = list(pack.screen_profiles.keys())[:3]
    assert len(fingerprints) >= 2
    
    for fp in fingerprints:
        html = rebuilder.generate_html_rebuild(fp)
        assert "<html" in html
        assert "phone-frame" in html
        assert pack.design_system.palette.primary_accent in html
        
        rebuilt_bytes = rebuilder.render_rebuild_image(fp)
        assert len(rebuilt_bytes) > 500
        
        # Save proof
        prof = pack.screen_profiles[fp]
        orig_bytes = screens[fp].screenshot_bytes
        proof_path = str(OUTPUT_DIR / f"test_fidelity_{prof['screen_name'].replace(' ', '_')}.png")
        saved = generate_side_by_side_fidelity_proof(orig_bytes, rebuilt_bytes, prof["screen_name"], proof_path)
        assert os.path.exists(saved)
