import json
import os

import streamlit as st

from src.analysis import DiagramAnalyzer
from src.enhancement import DiagramEnhancer
from src.generation import (
    MermaidAgent,
    MermaidAgentError,
    normalize_mermaid,
    render_mermaid_diagram,
)
from src.preprocessing import PromptOptimizer

st.set_page_config(
    page_title="LSEG Quant Challenge",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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


DEFAULT_COLORS = {
    "storage": "#378ADD",
    "compute": "#BA7517",
    "media": "#639922",
    "events": "#D4537E",
    "classifier": "#22c55e",
    "tools": "#ef4444",
}

EXAMPLES = [
    "CI/CD pipeline with GitHub repos, Jenkins CI, Docker build, and AWS ECS deployment",
    "RAG application: user query -> embedding -> vector DB -> LLM -> response",
    "Trading workflow where a user submits an order, the risk engine validates it, and the execution venue confirms it",
]

CAT_ICONS = {
    "layout": "📐",
    "labels": "🏷️",
    "styling": "🎨",
    "completeness": "🧩",
    "best-practice": "✅",
}


def inject_styles() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp, header[data-testid="stHeader"] {
    background:
        radial-gradient(circle at top left, rgba(99, 102, 241, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(16, 185, 129, 0.12), transparent 26%),
        #0e0e14 !important;
}

section[data-testid="stSidebar"] {
    display: none;
}

[data-testid="stAppViewContainer"] > .main {
    padding-top: 1.5rem;
}

[data-testid="column"] > div[data-testid="stVerticalBlock"] {
    background: rgba(19, 19, 29, 0.88);
    border: 1px solid #1e1e2e;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
    backdrop-filter: blur(18px);
}

.app-kicker {
    color: #818cf8;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.app-title {
    font-size: 32px;
    line-height: 1.05;
    font-weight: 700;
    color: #eef2ff;
    margin-bottom: 8px;
}

.app-subtitle {
    font-size: 14px;
    color: #94a3b8;
    margin-bottom: 20px;
    max-width: 36rem;
}

.section-label {
    color: #64748b;
    font-size: 11px;
    margin-bottom: 8px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.stTextArea textarea {
    background-color: #13131d !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    font-size: 14px !important;
    padding: 14px !important;
}

.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.25) !important;
}

.stTextArea label,
.stColorPicker label {
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    min-height: 42px !important;
}

.stButton > button[kind="primary"] {
    border: none !important;
    background: linear-gradient(135deg, #6366f1, #14b8a6) !important;
    color: white !important;
}

.chip-btn .stButton > button {
    background: transparent !important;
    border: 1px solid #2a2a3a !important;
    color: #94a3b8 !important;
    min-height: 38px !important;
    border-radius: 999px !important;
    padding: 0 12px !important;
}

.chip-btn .stButton > button:hover {
    border-color: #6366f1 !important;
    color: #c7d2fe !important;
    background-color: rgba(99, 102, 241, 0.08) !important;
}

.metric-card {
    background: linear-gradient(180deg, rgba(17, 24, 39, 0.9), rgba(15, 23, 42, 0.68));
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 14px 16px;
    min-height: 120px;
}

.metric-title {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.metric-value {
    color: #e2e8f0;
    font-size: 13px;
}

.metric-value ul {
    margin: 0;
    padding-left: 18px;
}

.metric-value li {
    margin-bottom: 4px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background-color: #13131d;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #1e1e2e;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #64748b;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 18px;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #1e1e2e;
    color: #e2e8f0;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

[data-testid="stExpander"] {
    border: 1px solid #1e1e2e !important;
    border-radius: 14px !important;
    background-color: #13131d !important;
}

.streamlit-expanderHeader {
    color: #cbd5e1 !important;
    font-size: 13px !important;
}

.stCodeBlock {
    border-radius: 14px !important;
}

.stCodeBlock code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #cbd5e1;
    background: rgba(30, 41, 59, 0.65);
    border: 1px solid #334155;
    border-radius: 999px;
    padding: 8px 12px;
    font-size: 12px;
    margin-bottom: 12px;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 560px;
    color: #334155;
    text-align: center;
}

.empty-state-symbol {
    font-size: 72px;
    margin-bottom: 18px;
    opacity: 0.55;
}

.empty-state-title {
    font-size: 18px;
    font-weight: 600;
    color: #475569;
    margin-bottom: 8px;
}

.empty-state-body {
    font-size: 13px;
    color: #334155;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    defaults = {
        "prompt_area": "",
        "current_diagram": None,
        "current_raw_mermaid": None,
        "current_description": None,
        "current_refined": None,
        "current_analysis": None,
        "current_cache_key": None,
        "current_step_status": [],
        "current_suggestions": None,
        "accepted_suggestion_ids": set(),
        "edit_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_working_state() -> None:
    st.session_state.current_diagram = None
    st.session_state.current_raw_mermaid = None
    st.session_state.current_description = None
    st.session_state.current_refined = None
    st.session_state.current_analysis = None
    st.session_state.current_cache_key = None
    st.session_state.current_step_status = []
    st.session_state.current_suggestions = None
    st.session_state.accepted_suggestion_ids = set()
    st.session_state.edit_history = []


def format_list(items: list[str], empty_text: str = "None") -> str:
    if not items:
        return f"<p>{empty_text}</p>"
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def load_cached_diagram(cache_key: str) -> None:
    refined, analysis, diagram = st.session_state[cache_key]
    st.session_state.current_cache_key = cache_key
    st.session_state.current_description = cache_key.split("diagram::", 1)[1]
    st.session_state.current_refined = refined
    st.session_state.current_analysis = analysis
    st.session_state.current_diagram = diagram
    st.session_state.current_raw_mermaid = diagram
    st.session_state.current_step_status = [
        "Prompt refinement cached",
        "Architecture analysis cached",
        "Diagram generation cached",
    ]
    st.session_state.current_suggestions = None
    st.session_state.accepted_suggestion_ids = set()
    st.session_state.edit_history = []


def generate_diagram(description: str) -> None:
    raw = description.strip()
    cache_key = f"diagram::{raw}"

    if cache_key in st.session_state:
        load_cached_diagram(cache_key)
        return

    refined = get_optimizer().optimize(raw)
    analysis = get_analyzer().analyze(refined)
    analysis_json = json.dumps(analysis.model_dump(), indent=2)

    raw_mermaid = ""
    placeholder = st.empty()
    try:
        for chunk in get_mermaid_agent().stream_diagram(refined, analysis_json):
            raw_mermaid += chunk
            placeholder.code(raw_mermaid, language="mermaid")
    finally:
        placeholder.empty()

    diagram = normalize_mermaid(raw_mermaid)
    st.session_state[cache_key] = (refined, analysis, diagram)
    st.session_state.current_cache_key = cache_key
    st.session_state.current_description = raw
    st.session_state.current_refined = refined
    st.session_state.current_analysis = analysis
    st.session_state.current_diagram = diagram
    st.session_state.current_raw_mermaid = raw_mermaid
    st.session_state.current_step_status = [
        "Prompt refined",
        "Architecture analyzed",
        "Diagram generated",
    ]
    st.session_state.current_suggestions = None
    st.session_state.accepted_suggestion_ids = set()
    st.session_state.edit_history = []


def render_analysis_cards(analysis) -> None:
    if analysis is None:
        return

    cards = [
        ("Diagram Type", f"<p>{analysis.diagram_type}</p>"),
        ("Components", format_list(analysis.components)),
        ("Relationships", format_list(analysis.relationships)),
        ("Decision Points", format_list(analysis.decision_points)),
        ("Inferred", format_list(analysis.inferred_components, "No gaps detected")),
        ("Best Practices", format_list(analysis.best_practices, "No guidance returned")),
    ]

    for row_start in range(0, len(cards), 3):
        cols = st.columns(3, gap="small")
        for col, (title, body) in zip(cols, cards[row_start : row_start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">{title}</div>
                        <div class="metric-value">{body}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def get_selected_colors() -> dict[str, str]:
    return {
        color_type: st.session_state.get(f"color_{color_type}", default)
        for color_type, default in DEFAULT_COLORS.items()
    }


def ensure_suggestions() -> list:
    suggestions = st.session_state.current_suggestions
    if suggestions is None and st.session_state.current_description and st.session_state.current_diagram:
        with st.spinner("Generating improvement suggestions..."):
            suggestions = get_enhancer().suggest(
                st.session_state.current_diagram,
                st.session_state.current_description,
            )
        st.session_state.current_suggestions = suggestions
    return suggestions or []


def apply_accepted_suggestions() -> None:
    suggestions = st.session_state.current_suggestions or []
    accepted_ids = st.session_state.accepted_suggestion_ids
    accepted = [s for s in suggestions if s.id in accepted_ids]
    if not accepted:
        return

    current = st.session_state.current_diagram
    with st.spinner("Applying accepted suggestions..."):
        merged = get_enhancer().apply_suggestions(current, accepted)
    st.session_state.edit_history.append(
        {"instruction": "Applied accepted suggestions", "diagram": current}
    )
    st.session_state.current_diagram = merged
    st.session_state.current_raw_mermaid = merged
    st.session_state.current_suggestions = None
    st.session_state.accepted_suggestion_ids = set()


inject_styles()
init_session_state()

left, right = st.columns([34, 66], gap="large")

with left:
    st.markdown('<div class="app-kicker">LSEG Quant Challenge</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-title">◈ Diagram Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Bring over the sharper UI, keep the richer pipeline. Describe a system in plain English and this branch still runs refinement, analysis, generation, suggestions, and freeform edits.</div>',
        unsafe_allow_html=True,
    )

    prompt = st.text_area(
        "Describe your system",
        height=170,
        placeholder="e.g. A trading workflow where an order enters risk checks, routes to the market, and reports fills back to the portfolio manager...",
        key="prompt_area",
    )

    st.markdown('<div class="section-label">Examples</div>', unsafe_allow_html=True)
    chip_cols = st.columns(3, gap="small")
    for i, example in enumerate(EXAMPLES):
        with chip_cols[i]:
            short_label = example.split(":")[0].split(" where ")[0].split(" with ")[0].strip()
            st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
            st.button(
                short_label,
                key=f"example_{i}",
                use_container_width=True,
                on_click=lambda ex=example: st.session_state.update({"prompt_area": ex}),
            )
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    with st.expander("🎨 Node Colors", expanded=False):
        color_cols = st.columns(2, gap="small")
        for idx, (color_type, default) in enumerate(DEFAULT_COLORS.items()):
            with color_cols[idx % 2]:
                st.color_picker(
                    color_type.capitalize(),
                    value=default,
                    key=f"color_{color_type}",
                )

    if st.button("⬡ Generate Diagram", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.warning("Please describe a system first.", icon="⚠️")
        else:
            reset_working_state()
            try:
                generate_diagram(prompt)
            except MermaidAgentError as exc:
                st.error(str(exc))

    if st.session_state.current_step_status:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
        for step in st.session_state.current_step_status:
            st.markdown(
                f'<div class="status-pill">● {step}</div>',
                unsafe_allow_html=True,
            )

with right:
    if st.session_state.current_diagram:
        colors = get_selected_colors()
        tab_diagram, tab_code, tab_analysis, tab_enhance = st.tabs(
            ["◈ Diagram", "{ } Mermaid Code", "Analysis", "Enhance"]
        )

        with tab_diagram:
            render_mermaid_diagram(
                st.session_state.current_diagram,
                height=640,
                colors=colors,
            )

        with tab_code:
            st.code(st.session_state.current_raw_mermaid, language="mermaid")
            if st.session_state.current_refined:
                with st.expander("Refined prompt"):
                    st.write(st.session_state.current_refined)

        with tab_analysis:
            render_analysis_cards(st.session_state.current_analysis)

        with tab_enhance:
            suggestions = ensure_suggestions()
            if not suggestions:
                st.info("No suggestions available for the current diagram.")
            else:
                for suggestion in suggestions:
                    already_accepted = suggestion.id in st.session_state.accepted_suggestion_ids
                    icon = CAT_ICONS.get(suggestion.category, "💡")
                    with st.expander(
                        f"{icon} {suggestion.title} ({suggestion.category})"
                        + (" • selected" if already_accepted else ""),
                        expanded=not already_accepted,
                    ):
                        st.write(suggestion.description)
                        with st.popover("Preview change"):
                            st.code(suggestion.updated_diagram, language="mermaid")
                            render_mermaid_diagram(
                                suggestion.updated_diagram,
                                height=320,
                                colors=colors,
                            )
                        if not already_accepted:
                            if st.button(
                                "Select suggestion",
                                key=f"accept_{suggestion.id}",
                            ):
                                st.session_state.accepted_suggestion_ids.add(suggestion.id)
                                st.rerun()

                if st.session_state.accepted_suggestion_ids:
                    if st.button("Apply selected suggestions", type="primary"):
                        apply_accepted_suggestions()
                        st.rerun()

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Natural Language Edit</div>', unsafe_allow_html=True)
            with st.form("freeform-edit", clear_on_submit=True):
                instruction = st.text_area(
                    "Describe how to modify the diagram",
                    placeholder="e.g. Add an exception handling branch from the risk engine back to the trader, then highlight the decision nodes.",
                    height=110,
                )
                edit_submitted = st.form_submit_button("Apply change")

            if edit_submitted and instruction.strip():
                current = st.session_state.current_diagram
                with st.spinner("Applying your change..."):
                    updated = get_enhancer().freeform_edit(
                        current,
                        instruction.strip(),
                    )
                st.session_state.edit_history.append(
                    {"instruction": instruction.strip(), "diagram": current}
                )
                st.session_state.current_diagram = updated
                st.session_state.current_raw_mermaid = updated
                st.session_state.current_suggestions = None
                st.session_state.accepted_suggestion_ids = set()
                st.rerun()

            if st.session_state.edit_history:
                with st.expander(f"Edit history ({len(st.session_state.edit_history)} edit(s))"):
                    for i, entry in enumerate(st.session_state.edit_history, 1):
                        st.markdown(f"**{i}.** {entry['instruction']}")

                if st.button("Undo last edit"):
                    last = st.session_state.edit_history.pop()
                    st.session_state.current_diagram = last["diagram"]
                    st.session_state.current_raw_mermaid = last["diagram"]
                    st.session_state.current_suggestions = None
                    st.session_state.accepted_suggestion_ids = set()
                    st.rerun()
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-symbol">◈</div>
                <div class="empty-state-title">No diagram yet</div>
                <div class="empty-state-body">
                    Describe your system on the left and generate a diagram to see the imported UI in action.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
