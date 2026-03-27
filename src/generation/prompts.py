from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """You convert natural language descriptions into Mermaid diagrams.

Return Mermaid code only.
Do not include Markdown code fences.
Prefer concise node labels.
Use the diagram type specified in the analysis.
Include all components, relationships, and decision points from the analysis.
Apply the best practices listed in the analysis.

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
