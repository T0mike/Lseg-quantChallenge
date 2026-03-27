from __future__ import annotations

from .exceptions import MermaidValidationError


KNOWN_DIAGRAM_PREFIXES = (
    "flowchart",
    "graph",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "mindmap",
    "timeline",
    "gitGraph",
    "requirementDiagram",
    "quadrantChart",
    "xychart-beta",
    "sankey-beta",
    "packet-beta",
    "block-beta",
    "architecture-beta",
    "kanban",
)


def strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def normalize_mermaid(text: str) -> str:
    candidate = strip_code_fences(text)
    if not candidate:
        raise MermaidValidationError("The model returned an empty Mermaid diagram.")

    first_line = candidate.splitlines()[0].strip()
    if first_line.startswith(KNOWN_DIAGRAM_PREFIXES):
        return candidate

    if any(token in candidate for token in ("-->", "---", "==>", "-.->")):
        return f"flowchart TD\n{candidate}"

    raise MermaidValidationError(
        "The generated output is not recognized as valid Mermaid syntax."
    )
