import json
import os
import sys
from pathlib import Path
import streamlit as st
from PIL import Image

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from common.config import OUTPUT_DIR
from layer7_compiler.compiler import AppKnowledgePack
from layer9_rebuild.rebuilder import ScreenRebuilder

st.set_page_config(
    page_title="RevRag Zero-Touch Knowledge Viewer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Sleek Dark Theme
st.markdown("""
<style>
    .stApp {
        background-color: #0b0d14;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    .metric-card {
        background: #151824;
        border: 1px solid #262c40;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .metric-val {
        font-size: 26px;
        font-weight: 700;
        color: #6366f1;
    }
    .metric-lbl {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        background: #312e81;
        color: #c7d2fe;
        margin-right: 6px;
    }
    .color-swatch {
        display: inline-block;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        vertical-align: middle;
        margin-right: 8px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

def load_latest_knowledge_pack() -> tuple[dict, AppKnowledgePack | None]:
    pack_file = OUTPUT_DIR / "knowledge_pack.json"
    if not pack_file.exists():
        pack_file = OUTPUT_DIR / "test_knowledge_pack.json"
    
    if pack_file.exists():
        with open(pack_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data, AppKnowledgePack.model_validate(data)
    return {}, None

pack_dict, pack_obj = load_latest_knowledge_pack()

st.sidebar.title("⚡ RevRag In-App Agent")
st.sidebar.caption("PS-002: Zero-Touch App Understanding")

if not pack_obj:
    st.warning("No compiled Knowledge Pack found in `./output/`. Run the pipeline first:")
    st.code("python run.py --mode mock", language="bash")
    if st.button("🚀 Run Mock Pipeline Now"):
        with st.spinner("Executing autonomous exploration and compilation..."):
            from run import run_pipeline
            run_pipeline(mode="mock", package_name="com.revrag.sampleapp")
            st.rerun()
    st.stop()

metadata = pack_obj.metadata
design = pack_obj.design_system
graph = pack_obj.screen_graph
profiles = pack_obj.screen_profiles

# Top Stats Header
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{metadata.package_name.split(".")[-1]}</div><div class="metric-lbl">Target Package</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{metadata.total_screens_discovered}</div><div class="metric-lbl">Discovered Screens</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{metadata.total_transitions_logged}</div><div class="metric-lbl">Transition Edges</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{metadata.pack_size_kb} KB</div><div class="metric-lbl">Pack Size (&lt;1.5MB)</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{metadata.compression_ratio}</div><div class="metric-lbl">Tree Compression</div></div>', unsafe_allow_html=True)

tab_viewer, tab_graph, tab_design, tab_rebuild, tab_json = st.tabs([
    "📱 Screen Explorer & Profiles",
    "🗺️ App Journey Graph",
    "🎨 Brand & Design System",
    "🔄 Fidelity & Rebuild Proof",
    "📄 Raw JSON Schema Pack"
])

# TAB 1: Screen Explorer
with tab_viewer:
    screen_keys = list(profiles.keys())
    screen_names = [f"{profiles[k]['screen_name']} ({k[:10]}...)" for k in screen_keys]
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("Discovered Screens")
        selected_idx = st.radio("Select Screen to Inspect:", range(len(screen_keys)), format_func=lambda i: screen_names[i])
        selected_fp = screen_keys[selected_idx]
        selected_profile = profiles[selected_fp]

    with col_right:
        st.subheader(f"Screen Profile: {selected_profile['screen_name']}")
        st.markdown(f"<span class='badge'>{selected_profile['screen_category'].upper()}</span> <span class='badge'>FP: {selected_fp}</span>", unsafe_allow_html=True)
        
        st.markdown(f"**🎯 Screen Purpose:**")
        st.info(selected_profile['purpose'])
        
        if selected_profile.get("key_actions"):
            st.markdown("**⚡ Key Actions:**")
            for act in selected_profile["key_actions"]:
                st.markdown(f"- {act}")

        # Visual screenshot & Rebuild Side-by-Side
        sc_col1, sc_col2 = st.columns(2)
        rebuilder = ScreenRebuilder(pack_obj)

        with sc_col1:
            st.markdown("##### 📷 Captured Screenshot")
            sc_path = OUTPUT_DIR / f"screenshot_{selected_fp}.png"
            if sc_path.exists():
                st.image(str(sc_path))
            else:
                st.caption("Screenshot file rendered dynamically in simulation.")

        with sc_col2:
            st.markdown("##### 🎨 Knowledge Pack Rebuild")
            rebuilt_img_bytes = rebuilder.render_rebuild_image(selected_fp)
            st.image(rebuilt_img_bytes)

        st.markdown("##### 🧩 Extracted UI Elements & Form Semantics")
        elements_data = []
        for el in selected_profile.get("elements", []):
            elements_data.append({
                "ID": el.get("element_id"),
                "Role": el.get("role"),
                "Form Field Type": el.get("form_field_type") or "-",
                "Description": el.get("plain_description"),
                "Text / Label": el.get("text") or "-"
            })
        st.dataframe(elements_data)

# TAB 2: App Journey Graph
with tab_graph:
    st.subheader("Autonomous Transition & Journey Graph")
    
    # Render Mermaid graph
    mermaid_lines = ["graph TD"]
    for node in graph.nodes:
        mermaid_lines.append(f'    {node.fingerprint[:8]}["{node.screen_name}<br/><small>{node.category}</small>"]')
    
    for edge in graph.edges:
        act_lbl = edge.action_type
        if edge.target_element_id:
            act_lbl += f": {edge.target_element_id}"
        mermaid_lines.append(f'    {edge.from_fingerprint[:8]} -->|"{act_lbl}"| {edge.to_fingerprint[:8]}')
    
    st.markdown(f"""
    ```mermaid
    {"\n".join(mermaid_lines)}
    ```
    """)

    st.subheader("Discovered User Journeys")
    for j in graph.journeys:
        with st.expander(f"🛣️ {j.journey_name} ({j.step_count} steps)"):
            st.write(j.description)
            st.code(" ➔ ".join([profiles.get(fp, {}).get("screen_name", fp[:8]) for fp in j.screen_sequence]))

# TAB 3: Design System
with tab_design:
    st.subheader("Extracted Brand & Design System")
    
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.markdown("#### 🎨 Color Palette")
        palette = design.palette
        st.markdown(f"<div class='metric-card'>"
                    f"<p><span class='color-swatch' style='background:{palette.primary_accent};'></span><strong>Primary Accent:</strong> <code>{palette.primary_accent}</code></p>"
                    f"<p><span class='color-swatch' style='background:{palette.secondary_accent};'></span><strong>Secondary Accent:</strong> <code>{palette.secondary_accent}</code></p>"
                    f"<p><span class='color-swatch' style='background:{palette.background};'></span><strong>Background:</strong> <code>{palette.background}</code></p>"
                    f"<p><span class='color-swatch' style='background:{palette.surface};'></span><strong>Surface:</strong> <code>{palette.surface}</code></p>"
                    f"<p><strong>Theme Mode:</strong> {'🌙 Dark Mode' if palette.is_dark_mode else '☀️ Light Mode'}</p>"
                    f"</div>", unsafe_allow_html=True)

    with c_p2:
        st.markdown("#### 📐 Typography & Spacing Rhythm")
        st.markdown(f"<div class='metric-card'>"
                    f"<p><strong>Base Grid Unit:</strong> {design.spacing.base_grid_unit_dp} dp</p>"
                    f"<p><strong>Screen Padding:</strong> {design.spacing.screen_padding_horizontal_dp} dp</p>"
                    f"<p><strong>Border Radius:</strong> {design.spacing.border_radius_dp} dp</p>"
                    f"<p><strong>Font Family:</strong> <code>{design.typography.font_family_recommendation}</code></p>"
                    f"</div>", unsafe_allow_html=True)

    st.markdown("#### 🗣️ Brand Tone of Voice")
    st.info(design.tone_of_voice)

    st.markdown("#### 📦 Recurring Component Catalog")
    st.dataframe([c.model_dump() for c in design.recurring_components])

# TAB 4: Rebuild Proof
with tab_rebuild:
    st.subheader("Visual Rebuild Proof (HTML/CSS Recreated Purely from JSON)")
    st.write("These visual reconstructions are generated 100% autonomously from the App Knowledge Pack JSON with zero access to original runtime pixel captures.")
    
    rebuild_files = list(OUTPUT_DIR.glob("fidelity_comparison_*.png")) + list(OUTPUT_DIR.glob("test_fidelity_*.png"))
    if rebuild_files:
        for f in rebuild_files[:4]:
            st.image(str(f))
    else:
        st.info("Run `python run.py` to generate complete side-by-side fidelity comparison exports.")

# TAB 5: Raw JSON
with tab_json:
    st.subheader("Complete Structured Knowledge Pack (JSON)")
    st.json(pack_dict)
