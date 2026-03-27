import json
import os

import streamlit as st

from src.analysis import DiagramAnalyzer
from src.generation import MermaidAgent, MermaidAgentError, normalize_mermaid, render_mermaid_diagram
from src.preprocessing import PromptOptimizer

st.set_page_config(page_title="LSEG Quant Challenge", layout="centered")

for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    if key in st.secrets and key not in os.environ:
        os.environ[key] = st.secrets[key]


@st.cache_resource
def get_optimizer() -> PromptOptimizer:
    return PromptOptimizer.from_env()


@st.cache_resource
def get_analyzer() -> DiagramAnalyzer:
    return DiagramAnalyzer.from_env()


@st.cache_resource
def get_mermaid_agent() -> MermaidAgent:
    return MermaidAgent.from_env()


st.title("LSEG Quant Challenge")
st.write("Generate Mermaid diagrams from natural language.")

with st.form("diagram-generator"):
    description = st.text_area(
        "Describe the diagram you want",
        placeholder=(
            "Example: Show a trading workflow where a user submits an order, "
            "the risk engine validates it, and the execution venue confirms it."
        ),
        height=160,
    )
    submitted = st.form_submit_button("Generate diagram")

if submitted:
    if not description.strip():
        st.warning("Enter a description before generating a diagram.")
    else:
        raw = description.strip()
        cache_key = f"diagram::{raw}"

        try:
            if cache_key in st.session_state:
                refined, analysis, diagram = st.session_state[cache_key]
                st.caption("Loaded from cache.")
            else:
                # Step 1: Refine
                with st.status("Step 1 — Refining prompt...") as status:
                    refined = get_optimizer().optimize(raw)
                    st.write(refined)
                    status.update(label="Step 1 — Prompt refined.", state="complete")

                # Step 2: Analyze
                with st.status("Step 2 — Analyzing architecture...") as status:
                    analysis = get_analyzer().analyze(refined)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Diagram type:** `{analysis.diagram_type}`")
                        st.markdown("**Components:**")
                        for c in analysis.components:
                            st.markdown(f"- {c.name} `{c.shape}`")
                        st.markdown("**Missing components:**")
                        for c in analysis.missing_components:
                            st.markdown(f"- {c.name} `{c.shape}`")
                    with col2:
                        st.markdown("**Relationships:**")
                        for r in analysis.relationships:
                            st.markdown(f"- {r}")
                        st.markdown("**Decision points:**")
                        for d in analysis.decision_points:
                            st.markdown(f"- {d}")
                        st.markdown("**Best practices:**")
                        for b in analysis.best_practices:
                            st.markdown(f"- {b}")
                    status.update(label="Step 2 — Architecture analyzed.", state="complete")

                # Step 3: Generate with streaming
                with st.status("Step 3 — Generating diagram...") as status:
                    analysis_json = json.dumps(analysis.model_dump(), indent=2)
                    raw_mermaid = ""
                    placeholder = st.empty()
                    for chunk in get_mermaid_agent().stream_diagram(refined, analysis_json):
                        raw_mermaid += chunk
                        placeholder.code(raw_mermaid, language="mermaid")
                    placeholder.empty()
                    diagram = normalize_mermaid(raw_mermaid)
                    status.update(label="Step 3 — Diagram generated.", state="complete")

                st.session_state[cache_key] = (refined, analysis, diagram)

            st.subheader("Diagram")
            render_mermaid_diagram(diagram)
            with st.expander("Mermaid source"):
                st.code(diagram, language="mermaid")

        except MermaidAgentError as exc:
            st.error(str(exc))
