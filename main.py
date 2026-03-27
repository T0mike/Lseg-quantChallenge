import streamlit as st

from src.preprocessing import PromptOptimizer
from src.generation import MermaidAgent, MermaidAgentError, normalize_mermaid, render_mermaid_diagram


st.set_page_config(page_title="LSEG Quant Challenge", layout="centered")


@st.cache_resource
def get_optimizer() -> PromptOptimizer:
    return PromptOptimizer.from_env()


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
                diagram = st.session_state[cache_key]
                st.caption("Loaded from cache.")
            else:
                # Step 1: optimize the prompt
                with st.status("Optimizing prompt...") as status:
                    optimized = get_optimizer().optimize(raw)
                    st.write(f"**Optimized:** {optimized}")
                    status.update(label="Prompt optimized.", state="complete")

                # Step 2: generate diagram with streaming
                raw_mermaid = ""
                placeholder = st.empty()
                for chunk in get_mermaid_agent().stream_diagram(optimized):
                    raw_mermaid += chunk
                    placeholder.code(raw_mermaid, language="mermaid")
                placeholder.empty()

                diagram = normalize_mermaid(raw_mermaid)
                st.session_state[cache_key] = diagram

            st.subheader("Diagram")
            render_mermaid_diagram(diagram)
            with st.expander("Mermaid source"):
                st.code(diagram, language="mermaid")
        except MermaidAgentError as exc:
            st.error(str(exc))
