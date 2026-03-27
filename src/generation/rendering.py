from __future__ import annotations

import json
import uuid

import streamlit.components.v1 as components


def render_mermaid_diagram(diagram: str, height: int = 420) -> None:
    container_id = f"mermaid-{uuid.uuid4().hex}"
    serialized_diagram = json.dumps(diagram)

    html = f"""
    <div id="{container_id}" class="mermaid"></div>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

      const container = document.getElementById("{container_id}");
      container.textContent = {serialized_diagram};

      mermaid.initialize({{
        startOnLoad: false,
        securityLevel: "loose",
        theme: "neutral",
      }});

      try {{
        await mermaid.run({{ nodes: [container] }});
      }} catch (error) {{
        container.innerHTML = `<pre style="white-space: pre-wrap; color: #b91c1c;">${{error}}</pre>`;
      }}
    </script>
    """

    components.html(html, height=height, scrolling=False)
