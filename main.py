import streamlit as st

from src.naive import MermaidAgent, MermaidAgentError, render_mermaid_diagram


st.set_page_config(page_title="LSEG Quant Challenge", layout="centered")


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
        try:
            with st.spinner("Generating Mermaid diagram..."):
                diagram = get_mermaid_agent().generate_diagram(description.strip())
            st.subheader("Diagram")
            render_mermaid_diagram(diagram)
            with st.expander("Mermaid source"):
                st.code(diagram, language="mermaid")
        except MermaidAgentError as exc:
            st.error(str(exc))
