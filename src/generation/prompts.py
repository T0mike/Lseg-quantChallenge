from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """You convert natural language descriptions into Mermaid diagrams.

Return Mermaid code only.
Do not include Markdown code fences.
Prefer concise node labels.
Always use flowchart TD. Never use sequenceDiagram, classDiagram, erDiagram, or any other diagram type.
Apply the best practices listed in the analysis.

CRITICAL — you MUST include ALL of the following in the diagram:
- Every component listed under "components" (explicitly mentioned in the description)
- Every component listed under "inferred_components" (logically necessary but not stated — add these even if the user did not mention them)
- Every relationship listed under "relationships"
- Every decision point listed under "decision_points"

The inferred_components are just as important as the explicit ones. A diagram that omits them is incomplete and wrong.

CRITICAL — use the correct Mermaid shape syntax for every node based on the shape field in the analysis:
  rectangle     → A[Text]
  rounded       → A(Text)
  diamond       → A{{Text}}
  cylinder      → A[(Text)]
  circle        → A((Text))
  asymmetric    → A>Text]
  parallelogram → A[/Text/]
  subroutine    → A[[Text]]

Never default all nodes to rectangles. Every node must use its assigned shape.

EDGE LABELS — add a short label (2-4 words max) only on arrows where the action is not obvious from context. Skip labels on self-evident transitions.

COLORS — add one classDef block at the end grouping nodes by shape type, then assign with class:
  classDef decision fill:#f59e0b,stroke:#d97706,color:#000
  classDef db        fill:#3b82f6,stroke:#2563eb,color:#fff
  classDef endpoint  fill:#10b981,stroke:#059669,color:#fff
  classDef external  fill:#f97316,stroke:#ea580c,color:#fff
  Only define classes that are actually used.
"""


def build_mermaid_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Generate a Mermaid diagram for this description:\n\n{description}\n\nArchitectural analysis:\n{analysis}",
            ),
        ],
    )
