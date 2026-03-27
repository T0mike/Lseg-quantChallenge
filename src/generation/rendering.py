from __future__ import annotations

import json
import uuid

import streamlit.components.v1 as components


def render_mermaid_diagram(
    diagram: str,
    height: int = 600,
    colors: dict[str, str] | None = None,
) -> None:
    if colors is None:
        colors = {}

    container_id = f"mermaid-{uuid.uuid4().hex}"
    serialized_diagram = json.dumps(diagram)
    colors_json = json.dumps(colors)

    html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{
        background: #0e0e14;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
      }}

      .toolbar {{
        display: flex;
        gap: 6px;
        padding: 10px;
        background: rgba(19, 19, 31, 0.96);
        border-bottom: 1px solid #1e1e2e;
      }}

      .toolbar button {{
        background: #1e1e2e;
        border: 1px solid #2a2a40;
        border-radius: 10px;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 12px;
        cursor: pointer;
        transition: background 0.15s ease, border-color 0.15s ease;
      }}

      .toolbar button:hover {{
        background: #2a2a40;
        border-color: #475569;
      }}

      .canvas-wrap {{
        width: 100%;
        height: calc(100vh - 48px);
        overflow: hidden;
        position: relative;
        background:
          radial-gradient(circle at top left, rgba(99, 102, 241, 0.12), transparent 24%),
          radial-gradient(circle at bottom right, rgba(20, 184, 166, 0.10), transparent 28%),
          #0e0e14;
        cursor: grab;
      }}

      .canvas-wrap::before {{
        content: "";
        position: absolute;
        inset: 0;
        background-image: radial-gradient(circle, rgba(51, 65, 85, 0.42) 1px, transparent 1px);
        background-size: 24px 24px;
        pointer-events: none;
      }}

      .canvas {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform-origin: center center;
        transform: translate(-50%, -50%) scale(1);
        transition: transform 0.1s ease;
        background: rgba(19, 19, 31, 0.95);
        border: 1px solid #1e1e2e;
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 20px 80px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(18px);
      }}

      .mermaid svg {{
        max-width: none !important;
        font-family: 'Inter', sans-serif !important;
      }}

      #detail-panel {{
        display: none;
        position: absolute;
        top: 14px;
        right: 14px;
        width: 260px;
        background: rgba(19, 19, 31, 0.98);
        border: 1px solid #2a2a40;
        border-radius: 14px;
        padding: 14px 16px;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: #e2e8f0;
        z-index: 100;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
      }}

      #detail-panel.visible {{ display: block; }}

      .detail-close {{
        float: right;
        cursor: pointer;
        color: #64748b;
        font-size: 16px;
        line-height: 1;
      }}

      .detail-close:hover {{ color: #e2e8f0; }}
    </style>

    <div class="toolbar">
      <button onclick="zoom(0.2)">+ Zoom in</button>
      <button onclick="zoom(-0.2)">- Zoom out</button>
      <button onclick="resetZoom()">Reset</button>
    </div>

    <div class="canvas-wrap" id="wrap">
      <div class="canvas" id="canvas">
        <div id="{container_id}" class="mermaid"></div>
      </div>
      <div id="detail-panel">
        <span id="detail-title" style="font-weight:600"></span>
        <span class="detail-close" onclick="document.getElementById('detail-panel').classList.remove('visible')">x</span>
        <div id="detail-body" style="margin-top:8px;color:#94a3b8;font-size:12px"></div>
      </div>
    </div>

    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

      const container = document.getElementById("{container_id}");
      const canvas = document.getElementById("canvas");
      const wrap = document.getElementById("wrap");
      const nodeColors = {colors_json};
      let scale = 1;
      let isDragging = false;
      let startX = 0;
      let startY = 0;
      let translateX = 0;
      let translateY = 0;

      window.zoom = (delta) => {{
        scale = Math.min(Math.max(scale + delta, 0.3), 3);
        updateTransform();
      }};

      window.resetZoom = () => {{
        scale = 1;
        translateX = 0;
        translateY = 0;
        updateTransform();
      }};

      function updateTransform() {{
        canvas.style.transform = `translate(calc(-50% + ${{translateX}}px), calc(-50% + ${{translateY}}px)) scale(${{scale}})`;
      }}

      wrap.addEventListener("wheel", (event) => {{
        event.preventDefault();
        zoom(event.deltaY < 0 ? 0.1 : -0.1);
      }}, {{ passive: false }});

      wrap.addEventListener("mousedown", (event) => {{
        isDragging = true;
        startX = event.clientX - translateX;
        startY = event.clientY - translateY;
        wrap.style.cursor = "grabbing";
      }});

      window.addEventListener("mousemove", (event) => {{
        if (!isDragging) {{
          return;
        }}
        translateX = event.clientX - startX;
        translateY = event.clientY - startY;
        updateTransform();
      }});

      window.addEventListener("mouseup", () => {{
        isDragging = false;
        wrap.style.cursor = "grab";
      }});

      container.textContent = {serialized_diagram};

      mermaid.initialize({{
        startOnLoad: false,
        securityLevel: "loose",
        theme: "dark",
        themeVariables: {{
          background: "#13131f",
          primaryColor: "#1e1e2e",
          primaryTextColor: "#e2e8f0",
          primaryBorderColor: "#334155",
          lineColor: "#818cf8",
          secondaryColor: "#16162a",
          tertiaryColor: "#0b0b11",
          fontSize: "14px",
          fontFamily: "Inter, sans-serif",
          edgeLabelBackground: "#13131f",
          clusterBkg: "#13131f",
          clusterBorder: "#334155",
          titleColor: "#e2e8f0",
          nodeTextColor: "#e2e8f0",
        }},
      }});

      try {{
        await mermaid.run({{ nodes: [container] }});
        setTimeout(() => {{
          container.querySelectorAll(".node").forEach((node) => {{
            const id = node.id || "";
            const typeMatch = Object.keys(nodeColors).find((type) => id.includes(type));
            if (typeMatch) {{
              const color = nodeColors[typeMatch];
              node.querySelectorAll("rect, polygon, circle, ellipse, path").forEach((shape) => {{
                shape.style.fill = color + "20";
                shape.style.stroke = color;
              }});
            }}

            node.style.cursor = "pointer";
            node.addEventListener("click", (event) => {{
              event.stopPropagation();
              const label = node.querySelector("span")?.innerText
                || node.querySelector("p")?.innerText
                || node.innerText
                || "";
              document.getElementById("detail-title").textContent = label.trim() || "Diagram node";
              document.getElementById("detail-body").textContent = "Interactive canvas imported from the UI branch. Drag to pan, use the wheel to zoom, and inspect nodes here.";
              document.getElementById("detail-panel").classList.add("visible");
            }});
          }});
        }}, 600);
      }} catch (error) {{
        container.innerHTML = `<pre style="white-space: pre-wrap; color: #ef4444; font-family: 'JetBrains Mono', monospace; font-size: 12px;">${{error}}</pre>`;
      }}
    </script>
    """

    components.html(html, height=height, scrolling=False)
