import streamlit as st
import anthropic
import json
import re

# ─── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Mermaid Diagram Generator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Default node colours ──────────────────────────────────────
DEFAULT_COLORS = {
    "storage": "#378ADD",
    "compute": "#BA7517",
    "media": "#639922",
    "events": "#D4537E",
    "classifier": "#22c55e",
    "tools": "#ef4444",
}

# ─── Session state initialisation ─────────────────────────────
if "mermaid_code" not in st.session_state:
    st.session_state.mermaid_code = ""
if "node_metadata" not in st.session_state:
    st.session_state.node_metadata = []
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None
if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""

EXAMPLES = [
    "CI/CD pipeline with GitHub repos, Jenkins CI, Docker build, and AWS ECS deployment",
    "RAG application: user query → embedding → vector DB → LLM → response",
    "Microservices: API gateway → auth service, user service, payment service → PostgreSQL & Redis",
]

# ─── Inject custom CSS ────────────────────────────────────────
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

/* ── Sidebar (hidden) ── */
section[data-testid="stSidebar"] { display: none; }

/* ── Text area ── */
.stTextArea textarea {
    background-color: #13131d !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 14px !important;
    transition: border-color 0.2s ease;
}
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 1px #6366f130 !important;
}
.stTextArea label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    letter-spacing: 0.02em;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    font-size: 13px !important;
}
/* Generate button (primary) */
.stButton > button[kind="primary"],
div[data-testid="stVerticalBlock"] > div:has(> .stButton) .stButton > button {
    border: none !important;
}
/* Example chip buttons */
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
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 13px;
    padding: 8px 20px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #1e1e2e;
    color: #e2e8f0;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

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

/* ── Color picker ── */
.stColorPicker label {
    color: #94a3b8 !important;
    font-size: 12px !important;
}

/* ── Code block ── */
.stCodeBlock {
    border-radius: 10px !important;
}
.stCodeBlock code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

/* ── Divider ── */
hr {
    border-color: #1e1e2e !important;
}

/* ── Detail panel ── */
.node-detail-panel {
    background-color: #13131d;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
    padding: 20px;
    margin-top: 12px;
}
.node-detail-panel h4 {
    margin: 0 0 4px 0;
    font-size: 15px;
    color: #e2e8f0;
}
.node-detail-panel .node-type-badge {
    display: inline-block;
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-weight: 500;
}
.node-detail-panel p {
    color: #94a3b8;
    font-size: 13px;
    line-height: 1.6;
    margin: 0;
}

/* ── Scrollbar ── */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0e0e14;
}
::-webkit-scrollbar-thumb {
    background: #2a2a3a;
    border-radius: 3px;
}

/* ── Title styling ── */
.app-title {
    font-size: 22px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 2px;
    letter-spacing: -0.02em;
}
.app-subtitle {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 24px;
    font-weight: 400;
}

/* ── Spinner ── */
.stSpinner > div > div {
    border-top-color: #6366f1 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────
# AI LOGIC
# ──────────────────────────────────────────────────────────────
def build_system_prompt(colors: dict[str, str]) -> str:
    color_list = "\n".join(f"  - {k}: {v}" for k, v in colors.items())
    return f"""You are a diagram architect. Given a natural language description, produce:
1. A Mermaid flowchart (graph LR) that accurately represents the system.
2. A JSON metadata block describing every node.

RULES:
- Always infer a response/return node if the flow implies one, even if the user didn't mention it.
- Assign each node one type from: storage, compute, media, events, classifier, tools
- Use the exact node IDs in both the Mermaid code and the JSON.
- If the user mentions specific colors for node types, override the defaults.
- Use subgraphs where logical grouping is appropriate.
- Keep node labels concise (2-4 words).
- Use meaningful edge labels where appropriate.

DEFAULT NODE COLORS (for reference):
{color_list}

OUTPUT FORMAT — respond with EXACTLY these two fenced blocks, nothing else:

```mermaid
graph LR
    ...
```

```json
{{
  "nodes": [
    {{"id": "nodeId", "label": "Node Label", "type": "compute", "description": "What this node does in the system."}},
    ...
  ]
}}
```
"""


def call_claude(user_text: str, colors: dict[str, str]) -> tuple[str, list[dict]]:
    """Send user text to Claude and return (mermaid_code, node_metadata)."""
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=4096,
        system=build_system_prompt(colors),
        messages=[{"role": "user", "content": user_text}],
    )

    full_text = response.content[0].text

    # Extract mermaid block
    mermaid_match = re.search(r"```mermaid\s*\n(.*?)```", full_text, re.DOTALL)
    mermaid_code = mermaid_match.group(1).strip() if mermaid_match else ""

    # Extract JSON block
    json_match = re.search(r"```json\s*\n(.*?)```", full_text, re.DOTALL)
    nodes = []
    if json_match:
        try:
            data = json.loads(json_match.group(1).strip())
            nodes = data.get("nodes", [])
        except json.JSONDecodeError:
            nodes = []

    return mermaid_code, nodes


# ──────────────────────────────────────────────────────────────
# MERMAID HTML COMPONENT
# ──────────────────────────────────────────────────────────────
def build_mermaid_html(mermaid_code: str, colors: dict[str, str], nodes: list[dict]) -> str:
    """Build the HTML/JS that renders Mermaid with custom dark styling."""

    # Build node→type mapping
    node_type_map = {n["id"]: n["type"] for n in nodes if "id" in n and "type" in n}
    node_type_json = json.dumps(node_type_map)
    colors_json = json.dumps(colors)
    nodes_json = json.dumps(nodes)

    # Escape backticks in mermaid for JS template literal
    escaped_mermaid = mermaid_code.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0e0e14;
    font-family: 'Inter', sans-serif;
    display: flex;
    justify-content: center;
    padding: 20px;
    min-height: 100px;
  }}
  #mermaid-container {{
    width: 100%;
    display: flex;
    justify-content: center;
  }}
  #mermaid-container svg {{
    max-width: 100%;
    height: auto;
  }}

  /* ── Mermaid node styling ── */
  .node rect, .node polygon, .node circle, .node ellipse {{
    stroke-width: 1.5px !important;
    rx: 8 !important;
    ry: 8 !important;
    filter: none !important;
  }}
  .node .label {{
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    fill: #e2e8f0 !important;
  }}

  /* ── Edges ── */
  .edgePath path.path {{
    stroke: #3a3a4a !important;
    stroke-width: 1.5px !important;
  }}
  .edgeLabel {{
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
    fill: #64748b !important;
    color: #64748b !important;
    background-color: #0e0e14 !important;
  }}
  .edgeLabel rect {{
    fill: #0e0e14 !important;
    opacity: 1 !important;
  }}

  /* ── Marker arrows ── */
  marker path {{
    fill: #3a3a4a !important;
  }}

  /* ── Subgraphs ── */
  .cluster rect {{
    fill: #13131d !important;
    stroke: #2a2a3a !important;
    stroke-width: 1px !important;
    rx: 12 !important;
    ry: 12 !important;
  }}
  .cluster span, .cluster text {{
    fill: #64748b !important;
    color: #64748b !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}

  /* ── Clickable nodes ── */
  .node {{
    cursor: pointer;
  }}
  .node:hover rect, .node:hover polygon {{
    filter: brightness(1.15) !important;
  }}
</style>
</head>
<body>
<div id="mermaid-container">
  <pre class="mermaid">
{escaped_mermaid}
  </pre>
</div>

<script>
const nodeTypeMap = {node_type_json};
const nodeColors = {colors_json};
const nodesData = {nodes_json};

mermaid.initialize({{
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {{
    darkMode: true,
    background: '#0e0e14',
    primaryColor: '#1e1e2e',
    primaryBorderColor: '#3a3a4a',
    primaryTextColor: '#e2e8f0',
    lineColor: '#3a3a4a',
    secondaryColor: '#13131d',
    tertiaryColor: '#13131d',
    fontSize: '13px',
    fontFamily: 'Inter, sans-serif',
    nodeBorder: '#3a3a4a',
  }},
  flowchart: {{
    curve: 'monotoneX',
    padding: 20,
    nodeSpacing: 50,
    rankSpacing: 60,
    htmlLabels: true,
    useMaxWidth: true,
  }},
  securityLevel: 'loose',
}});

async function renderDiagram() {{
  try {{
    const container = document.getElementById('mermaid-container');
    const {{ svg }} = await mermaid.render('mmd-diagram', `{escaped_mermaid}`);
    container.innerHTML = svg;

    // Apply colors per node type
    const svgEl = container.querySelector('svg');
    if (svgEl) {{
      const nodeEls = svgEl.querySelectorAll('.node');
      nodeEls.forEach(nodeEl => {{
        const id = nodeEl.id;
        // Mermaid wraps IDs: try to match
        for (const [nodeId, nodeType] of Object.entries(nodeTypeMap)) {{
          if (id && id.includes(nodeId)) {{
            const color = nodeColors[nodeType] || '#3a3a4a';
            const shapes = nodeEl.querySelectorAll('rect, polygon, circle, ellipse');
            shapes.forEach(s => {{
              s.style.fill = color + '20';
              s.style.stroke = color;
            }});
            break;
          }}
        }}

        // Click handler
        nodeEl.addEventListener('click', () => {{
          const clickedId = nodeEl.id;
          for (const node of nodesData) {{
            if (clickedId && clickedId.includes(node.id)) {{
              window.parent.postMessage({{
                type: 'mermaid-node-click',
                nodeId: node.id,
                label: node.label,
                nodeType: node.type,
                description: node.description
              }}, '*');
              break;
            }}
          }}
        }});
      }});

      // Resize iframe
      const bbox = svgEl.getBBox();
      const height = Math.max(bbox.height + 60, 300);
      document.body.style.height = height + 'px';
      window.parent.postMessage({{ type: 'streamlit:setFrameHeight', height: height }}, '*');
    }}
  }} catch (e) {{
    document.getElementById('mermaid-container').innerHTML =
      '<p style="color:#ef4444;font-family:Inter,sans-serif;font-size:13px;padding:20px;">Error rendering diagram: ' + e.message + '</p>';
  }}
}}

renderDiagram();
</script>
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────
# LAYOUT
# ──────────────────────────────────────────────────────────────
left, right = st.columns([35, 65], gap="large")

# ── LEFT PANEL ─────────────────────────────────────────────────
with left:
    st.markdown('<p class="app-title">◈ Diagram Generator</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="app-subtitle">Describe your system in plain English. AI turns it into a diagram.</p>',
        unsafe_allow_html=True,
    )

    prompt = st.text_area(
        "DESCRIBE YOUR SYSTEM",
        height=160,
        placeholder="e.g. A CI/CD pipeline with GitHub, Jenkins, Docker, and AWS deployment...",
        key="prompt_area",
    )

    # Example chips
    st.markdown(
        '<p style="color:#64748b;font-size:11px;margin-bottom:6px;font-weight:600;letter-spacing:0.05em;">EXAMPLES</p>',
        unsafe_allow_html=True,
    )
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

    # Color pickers (collapsed)
    with st.expander("🎨  Node Colors", expanded=False):
        color_cols = st.columns(2)
        colors = {}
        for idx, (ctype, default) in enumerate(DEFAULT_COLORS.items()):
            with color_cols[idx % 2]:
                colors[ctype] = st.color_picker(
                    ctype.capitalize(),
                    value=default,
                    key=f"color_{ctype}",
                )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Generate button
    generate = st.button(
        "⬡  Generate Diagram",
        use_container_width=True,
        type="primary",
        key="generate_btn",
    )

    if generate and prompt.strip():
        with st.spinner("Generating diagram..."):
            mermaid_code, nodes = call_claude(prompt.strip(), colors)
            st.session_state.mermaid_code = mermaid_code
            st.session_state.node_metadata = nodes
            st.session_state.selected_node = None
            st.session_state.user_prompt = prompt.strip()

    elif generate and not prompt.strip():
        st.warning("Please describe a system first.", icon="⚠️")

# ── RIGHT PANEL ────────────────────────────────────────────────
with right:
    if st.session_state.mermaid_code:
        tab_diagram, tab_code = st.tabs(["◈  Diagram", "{ }  Mermaid Code"])

        with tab_diagram:
            # Render Mermaid via HTML component
            html_content = build_mermaid_html(
                st.session_state.mermaid_code,
                colors if "colors" in dir() else DEFAULT_COLORS,
                st.session_state.node_metadata,
            )
            st.components.v1.html(html_content, height=600, scrolling=True)

            # Node click hint
            if st.session_state.node_metadata:
                st.markdown(
                    '<p style="color:#4a4a5a;font-size:11px;text-align:center;margin-top:4px;">'
                    "Click a node in the diagram to see its details</p>",
                    unsafe_allow_html=True,
                )

            # Node detail selector (fallback since postMessage → Streamlit is tricky)
            if st.session_state.node_metadata:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                node_labels = [f"{n.get('label', n['id'])}  ({n.get('type', '?')})" for n in st.session_state.node_metadata]
                selected_label = st.selectbox(
                    "Select node to inspect",
                    options=["— select a node —"] + node_labels,
                    key="node_select",
                    label_visibility="collapsed",
                )
                if selected_label != "— select a node —":
                    idx = node_labels.index(selected_label)
                    node = st.session_state.node_metadata[idx]
                    ntype = node.get("type", "compute")
                    ncolor = (colors if "colors" in dir() else DEFAULT_COLORS).get(ntype, "#6366f1")
                    st.markdown(
                        f"""<div class="node-detail-panel">
                            <h4>⬡ {node.get('label', node['id'])}</h4>
                            <span class="node-type-badge" style="background:{ncolor}30;color:{ncolor};border:1px solid {ncolor}50;">{ntype.upper()}</span>
                            <p>{node.get('description', 'No description available.')}</p>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        with tab_code:
            st.code(st.session_state.mermaid_code, language="mermaid")

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
