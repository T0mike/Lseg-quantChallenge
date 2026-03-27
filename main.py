import streamlit as st
from py_processing import PromptOptimizer
from src.naive import MermaidAgent, MermaidAgentError, normalize_mermaid, render_mermaid_diagram

# ─── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Mermaid Diagram Generator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Initialization ─────────────────────────────────────────────
@st.cache_resource
def get_optimizer() -> PromptOptimizer:
    return PromptOptimizer.from_env()

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
    "RAG application: user query → embedding → vector DB → LLM → response",
    "Microservices: API gateway → auth service, user service, payment service → PostgreSQL & Redis",
]

# ─── Inject custom CSS ─────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global overrides ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background-color: #0e0e14 !important;
}
header[data-testid="stHeader"] {
    background-color: #0e0e14 !important;
}
section[data-testid="stSidebar"] { display: none; }

/* ── Text area ── */
.stTextArea textarea {
    background-color: #13131d !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 14px !important;
    padding: 14px !important;
}
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 1px #6366f130 !important;
}
.stTextArea label {
    margin-bottom: 8px !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
.stButton > button[kind="primary"] {
    border: none !important;
}
.chip-btn .stButton > button {
    background-color: transparent !important;
    border: 1px solid #2a2a3a !important;
    color: #94a3b8 !important;
    padding: 4px 14px !important;
    font-size: 12px !important;
    border-radius: 20px !important;
}
.chip-btn .stButton > button:hover {
    border-color: #6366f1 !important;
    color: #c7d2fe !important;
    background-color: #6366f110 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
    background-color: #13131d;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #1e1e2e;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #64748b;
    font-weight: 500;
    font-size: 13px;
    padding: 8px 20px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #1e1e2e;
    color: #e2e8f0;
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: #13131d !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
    font-size: 13px !important;
}
[data-testid="stExpander"] {
    border: 1px solid #1e1e2e !important;
    border-radius: 10px !important;
    background-color: #13131d !important;
}
.stColorPicker label { font-size: 12px !important; color: #94a3b8 !important; }

/* ── Code block ── */
.stCodeBlock { border-radius: 10px !important; }
.stCodeBlock code { font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important; }

/* ── Title styling ── */
.app-title { font-size: 22px; font-weight: 700; color: #e2e8f0; margin-bottom: 2px; }
.app-subtitle { font-size: 13px; color: #64748b; margin-bottom: 24px; font-weight: 400; }
.stSpinner > div > div { border-top-color: #6366f1 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# LAYOUT
# ──────────────────────────────────────────────────────────────
left, right = st.columns([35, 65], gap="large")

# ── LEFT PANEL ─────────────────────────────────────────────────
with left:
    st.markdown('<p class="app-title">◈ Diagram Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Describe your system in plain English. AI turns it into a diagram.</p>', unsafe_allow_html=True)

    prompt = st.text_area(
        "Describe your system",
        height=160,
        placeholder="e.g. A CI/CD pipeline with GitHub, Jenkins, Docker, and AWS deployment...",
        key="prompt_area",
    )

    # Example chips
    st.markdown('<p style="color:#64748b;font-size:11px;margin-bottom:6px;font-weight:600;letter-spacing:0.05em;">EXAMPLES</p>', unsafe_allow_html=True)
    chip_cols = st.columns(3)
    for i, example in enumerate(EXAMPLES):
        with chip_cols[i]:
            short_label = example.split(":")[0].split(" with ")[0].strip()
            with st.container():
                st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                st.button(
                    short_label,
                    key=f"example_{i}",
                    use_container_width=True,
                    on_click=lambda ex=example: st.session_state.update({"prompt_area": ex}),
                )
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Color pickers
    with st.expander("🎨  Node Colors", expanded=False):
        color_cols = st.columns(2)
        colors = {}
        for idx, (ctype, default) in enumerate(DEFAULT_COLORS.items()):
            with color_cols[idx % 2]:
                colors[ctype] = st.color_picker(ctype.capitalize(), value=default, key=f"color_{ctype}")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    generate = st.button("⬡  Generate Diagram", use_container_width=True, type="primary", key="generate_btn")

# ── RIGHT PANEL ────────────────────────────────────────────────
with right:
    # Use session state to persist diagram results between reruns
    if "current_diagram" not in st.session_state:
        st.session_state.current_diagram = None
    if "current_raw_mermaid" not in st.session_state:
        st.session_state.current_raw_mermaid = None

    if generate:
        if not prompt.strip():
            st.warning("Please describe a system first.", icon="⚠️")
        else:
            raw = prompt.strip()
            cache_key = f"diagram::{raw}"
            
            with st.spinner("Generating..."):
                try:
                    if cache_key in st.session_state:
                        diagram = st.session_state[cache_key]
                        st.session_state.current_diagram = diagram
                        st.session_state.current_raw_mermaid = diagram
                    else:
                        # 1. Optimize
                        optimized = get_optimizer().optimize(raw)
                        
                        # 2. Stream into a temporary placeholder
                        st.markdown('<p style="color:#64748b;font-size:13px;margin-bottom:8px;">Streaming generation...</p>', unsafe_allow_html=True)
                        raw_mermaid = ""
                        placeholder = st.empty()
                        for chunk in get_mermaid_agent().stream_diagram(optimized):
                            raw_mermaid += chunk
                            placeholder.code(raw_mermaid, language="mermaid")
                        placeholder.empty() # Clear streaming output
                        
                        # 3. Process & Cache
                        diagram = normalize_mermaid(raw_mermaid)
                        st.session_state[cache_key] = diagram
                        st.session_state.current_diagram = diagram
                        st.session_state.current_raw_mermaid = raw_mermaid
                except MermaidAgentError as exc:
                    st.error(str(exc))

    # Display tabs if diagram exists
    if st.session_state.current_diagram:
        tab_diagram, tab_code = st.tabs(["◈  Diagram", "{ }  Mermaid Code"])
        with tab_diagram:
            render_mermaid_diagram(st.session_state.current_diagram, height=600, colors=colors)
        with tab_code:
            st.code(st.session_state.current_raw_mermaid, language="mermaid")
    else:
        # Empty state
        st.markdown(
            """
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                        height:500px;color:#2a2a3a;text-align:center;">
                <div style="font-size:64px;margin-bottom:16px;opacity:0.5;">◈</div>
                <p style="font-size:18px;font-weight:600;color:#3a3a4a;margin-bottom:8px;">
                    No diagram yet
                </p>
                <p style="font-size:13px;color:#2a2a3a;">
                    Describe your system on the left and click Generate
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
