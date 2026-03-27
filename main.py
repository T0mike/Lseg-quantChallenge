import json
import os

import streamlit as st

from src.analysis import DiagramAnalyzer
from src.enhancement import DiagramEnhancer
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
def get_enhancer() -> DiagramEnhancer:
    return DiagramEnhancer.from_env()


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

            # Step 4: Enhancement suggestions
            st.subheader("Enhancement Suggestions")

            suggestions_key = f"suggestions::{cache_key}"
            current_diagram_key = f"current_diagram::{cache_key}"

            # Keep the working diagram in session state
            if current_diagram_key not in st.session_state:
                st.session_state[current_diagram_key] = diagram

            # Generate suggestions if not cached
            if suggestions_key not in st.session_state:
                with st.spinner("Generating improvement suggestions..."):
                    suggestions = get_enhancer().suggest(diagram, raw)
                    st.session_state[suggestions_key] = suggestions
            else:
                suggestions = st.session_state[suggestions_key]

            if not suggestions:
                st.info("No suggestions — the diagram looks great!")
            else:
                # Category icons
                cat_icons = {
                    "layout": "\U0001f4d0",
                    "labels": "\U0001f3f7\ufe0f",
                    "styling": "\U0001f3a8",
                    "completeness": "\U0001f9e9",
                    "best-practice": "\u2705",
                }

                accepted_ids_key = f"accepted::{cache_key}"
                if accepted_ids_key not in st.session_state:
                    st.session_state[accepted_ids_key] = set()

                for suggestion in suggestions:
                    icon = cat_icons.get(suggestion.category, "\U0001f4a1")
                    already_accepted = (
                        suggestion.id in st.session_state[accepted_ids_key]
                    )

                    with st.expander(
                        f"{icon} {suggestion.title} ({suggestion.category})"
                        + (" — applied" if already_accepted else ""),
                        expanded=not already_accepted,
                    ):
                        st.write(suggestion.description)
                        with st.popover("Preview change"):
                            st.code(
                                suggestion.updated_diagram, language="mermaid"
                            )
                            render_mermaid_diagram(
                                suggestion.updated_diagram, height=300
                            )

                        if not already_accepted:
                            if st.button(
                                f"Accept",
                                key=f"accept_{suggestion.id}_{cache_key}",
                            ):
                                st.session_state[accepted_ids_key].add(
                                    suggestion.id
                                )
                                st.rerun()

                accepted_ids = st.session_state.get(accepted_ids_key, set())
                if accepted_ids:
                    accepted = [
                        s for s in suggestions if s.id in accepted_ids
                    ]

                    with st.spinner("Applying accepted suggestions..."):
                        current = st.session_state[current_diagram_key]
                        merged = get_enhancer().apply_suggestions(
                            current, accepted
                        )
                        st.session_state[current_diagram_key] = merged

                    st.subheader("Enhanced Diagram")
                    render_mermaid_diagram(merged)
                    with st.expander("Enhanced Mermaid source"):
                        st.code(merged, language="mermaid")

            # Step 5: Freeform natural-language edits
            st.subheader("Edit with Natural Language")
            current = st.session_state.get(current_diagram_key, diagram)

            edit_history_key = f"edit_history::{cache_key}"
            if edit_history_key not in st.session_state:
                st.session_state[edit_history_key] = []

            with st.form("freeform-edit", clear_on_submit=True):
                instruction = st.text_area(
                    "Describe how to modify the diagram",
                    placeholder=(
                        "Example: Add an error handling path from the risk engine "
                        "back to the user. Color all decision nodes in yellow."
                    ),
                    height=100,
                )
                edit_submitted = st.form_submit_button("Apply change")

            if edit_submitted and instruction.strip():
                with st.spinner("Applying your change..."):
                    updated = get_enhancer().freeform_edit(
                        current, instruction.strip()
                    )
                    st.session_state[edit_history_key].append(
                        {"instruction": instruction.strip(), "diagram": current}
                    )
                    st.session_state[current_diagram_key] = updated
                    st.rerun()

            # Show current working diagram if edits were applied
            edit_history = st.session_state.get(edit_history_key, [])
            if edit_history:
                st.subheader("Current Diagram")
                render_mermaid_diagram(current)
                with st.expander("Current Mermaid source"):
                    st.code(current, language="mermaid")

                with st.expander(f"Edit history ({len(edit_history)} edit(s))"):
                    for i, entry in enumerate(edit_history, 1):
                        st.markdown(f"**{i}.** {entry['instruction']}")

                if st.button("Undo last edit", key=f"undo_{cache_key}"):
                    last = st.session_state[edit_history_key].pop()
                    st.session_state[current_diagram_key] = last["diagram"]
                    st.rerun()

        except MermaidAgentError as exc:
            st.error(str(exc))
