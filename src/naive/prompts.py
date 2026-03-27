from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """You convert natural language descriptions into Mermaid diagrams.

Return Mermaid code only.
Do not include Markdown code fences.
Prefer concise node labels.
Choose the Mermaid diagram type that best matches the request.
If the request is ambiguous, default to a flowchart.
"""


def build_mermaid_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Generate a Mermaid diagram for this description:\n\n{description}",
            ),
        ],
    )
