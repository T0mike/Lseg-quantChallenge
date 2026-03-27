from __future__ import annotations
import json
import uuid
import streamlit.components.v1 as components

def render_mermaid_diagram(diagram: str, height: int = 600, colors: dict[str, str] | None = None) -> None:
    if colors is None:
        colors = {}
    
    container_id = f"mermaid-{uuid.uuid4().hex}"
    serialized_diagram = json.dumps(diagram)
    colors_json = json.dumps(colors)
    html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{ background: #0e0e14; overflow: hidden; }}
      
      .toolbar {{
        display: flex;
        gap: 6px;
        padding: 8px;
        background: #13131f;
        border-bottom: 0.5px solid #1e1e2e;
      }}
      
      .toolbar button {{
        background: #1e1e2e;
        border: 0.5px solid #2a2a40;
        border-radius: 6px;
        color: #e2e2f0;
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        padding: 4px 10px;
        cursor: pointer;
        transition: background 0.15s;
      }}
      .toolbar button:hover {{ background: #2a2a40; }}

      .canvas-wrap {{
        width: 100%;
        height: calc(100vh - 42px);
        overflow: hidden;
        position: relative;
        background: #0e0e14;
        background-image: radial-gradient(circle, #1e1e2e 1px, transparent 1px);
        background-size: 24px 24px;
      }}

      .canvas {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform-origin: center center;
        transform: translate(-50%, -50%) scale(1);
        transition: transform 0.1s;
        background: #13131f;
        border: 0.5px solid #1e1e2e;
        border-radius: 16px;
        padding: 32px;
      }}

      .mermaid svg {{
        max-width: none !important;
        font-family: 'Inter', sans-serif !important;
      }}

      #detail-panel {{
        display: none;
        position: absolute;
        top: 12px;
        right: 12px;
        width: 240px;
        background: #13131f;
        border: 0.5px solid #2a2a40;
        border-radius: 10px;
        padding: 12px 16px;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: #e2e2f0;
        z-index: 100;
      }}
      #detail-panel.visible {{ display: block; }}
      .detail-close {{
        float: right;
        cursor: pointer;
        color: #4b4b6e;
        font-size: 16px;
        line-height: 1;
      }}
      .detail-close:hover {{ color: #e2e2f0; }}
    </style>

    <div class="toolbar">
      <button onclick="zoom(0.2)">＋ Zoom in</button>
      <button onclick="zoom(-0.2)">－ Zoom out</button>
      <button onclick="resetZoom()">⊡ Reset</button>
    </div>

    <div class="canvas-wrap" id="wrap">
      <div class="canvas" id="canvas">
        <div id="{container_id}" class="mermaid"></div>
      </div>
      <div id="detail-panel">
        <span id="detail-title" style="font-weight:500"></span>
        <span class="detail-close" onclick="document.getElementById('detail-panel').classList.remove('visible')">×</span>
        <div id="detail-body" style="margin-top:6px;color:#8888aa;font-size:12px"></div>
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
      let startX, startY, translateX = 0, translateY = 0;

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

      wrap.addEventListener('wheel', (e) => {{
        e.preventDefault();
        zoom(e.deltaY < 0 ? 0.1 : -0.1);
      }}, {{ passive: false }});

      wrap.addEventListener('mousedown', (e) => {{
        isDragging = true;
        startX = e.clientX - translateX;
        startY = e.clientY - translateY;
        wrap.style.cursor = 'grabbing';
      }});

      window.addEventListener('mousemove', (e) => {{
        if (!isDragging) return;
        translateX = e.clientX - startX;
        translateY = e.clientY - startY;
        updateTransform();
      }});

      window.addEventListener('mouseup', () => {{
        isDragging = false;
        wrap.style.cursor = 'default';
      }});

      container.textContent = {serialized_diagram};
      
      mermaid.initialize({{
        startOnLoad: false,
        securityLevel: "loose",
        theme: "dark",
        themeVariables: {{
          background: "#13131f",
          primaryColor: "#1e1e2e",
          primaryTextColor: "#e2e2f0",
          primaryBorderColor: "#2a2a40",
          lineColor: "#6366f1",
          secondaryColor: "#16162a",
          tertiaryColor: "#0b0b11",
          fontSize: "14px",
          fontFamily: "Inter, sans-serif",
          edgeLabelBackground: "#13131f",
          clusterBkg: "#13131f",
          clusterBorder: "#2a2a40",
          titleColor: "#e2e2f0",
          nodeTextColor: "#e2e2f0",
        }},
      }});

      try {{
        await mermaid.run({{ nodes: [container] }});
        setTimeout(() => {{
          container.querySelectorAll('.node').forEach(node => {{
            const id = node.id || '';
            const typeMatch = Object.keys(nodeColors).find(t => id.includes(t));
            if (typeMatch) {{
              const color = nodeColors[typeMatch];
              node.querySelectorAll('rect, polygon, circle, ellipse').forEach(s => {{
                s.style.fill = color + '20';
                s.style.stroke = color;
              }});
            }}
            node.style.cursor = 'pointer';
            node.addEventListener('click', (e) => {{
              e.stopPropagation();
              const label = node.querySelector('span')?.innerText
                         || node.querySelector('p')?.innerText
                         || node.innerText || '';
              document.getElementById('detail-title').textContent = label.trim();
              document.getElementById('detail-body').textContent = 'Click to explore this component.';
              document.getElementById('detail-panel').classList.add('visible');
            }});
          }});
        }}, 600);
      }} catch (error) {{
        container.innerHTML = `<pre style="color:#ef4444;font-family:'JetBrains Mono',monospace;font-size:12px">${{error}}</pre>`;
      }}
    </script>
    """
    components.html(html, height=height, scrolling=False)