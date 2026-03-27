from langchain_core.prompts import ChatPromptTemplate


SUGGEST_SYSTEM_PROMPT = """\
You are an expert Mermaid diagram reviewer and enhancer.

You receive a Mermaid diagram and the original user description.
Suggest concrete improvements to make the diagram clearer, more complete,
and more professional.

Categories of improvements:
- **layout**: Better flow direction, grouping, or subgraph organisation.
- **labels**: Clearer, more descriptive node or edge labels.
- **styling**: Appropriate colors, shapes, or class definitions.
- **completeness**: Missing nodes, edges, error paths, or decision branches.
- **best-practice**: Mermaid idioms, accessibility, or readability tips.

Rules:
- Each suggestion MUST include a fully updated Mermaid diagram that applies
  ONLY that single suggestion on top of the original diagram.
- Do NOT combine multiple suggestions into one diagram.
- Keep the diagram type unchanged unless the suggestion explicitly proposes
  a different type.
- Return valid Mermaid syntax only in the `updated_diagram` field —
  no code fences.
"""

APPLY_SYSTEM_PROMPT = """\
You are a Mermaid diagram editor.

You receive the current Mermaid diagram and a list of accepted suggestions
(each with its own updated diagram). Your job is to merge ALL accepted
changes into a single coherent Mermaid diagram.

Rules:
- Combine all accepted suggestions without conflicts.
- If two suggestions modify the same node or edge, prefer the one listed
  later (higher priority).
- Return valid Mermaid code only — no code fences, no explanation.
"""


def build_suggest_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", SUGGEST_SYSTEM_PROMPT),
            (
                "human",
                "Original description:\n{description}\n\n"
                "Current Mermaid diagram:\n{diagram}\n\n"
                "Suggest up to {max_suggestions} improvements. "
                "Return a JSON object with a `suggestions` array. "
                "Each element has: id (s1, s2, …), title, description, "
                "category, and updated_diagram.",
            ),
        ],
    )


def build_apply_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", APPLY_SYSTEM_PROMPT),
            (
                "human",
                "Current diagram:\n{diagram}\n\n"
                "Accepted suggestions:\n{accepted_suggestions}\n\n"
                "Merge all accepted changes into a single Mermaid diagram.",
            ),
        ],
    )
