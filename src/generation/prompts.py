from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """You convert natural language descriptions into Mermaid diagrams.

Return Mermaid code only.
Do not include Markdown code fences.
Prefer concise node labels.
Use the diagram type specified in the analysis.
Include all components, relationships, and decision points from the analysis.
Apply the best practices listed in the analysis.
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
