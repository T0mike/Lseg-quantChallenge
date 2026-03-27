from langchain_core.prompts import ChatPromptTemplate

ANALYZER_SYSTEM_PROMPT = """You are a senior software/systems architect with deep expertise in diagram design.

Given a refined diagram description, analyze it thoroughly and return a structured analysis.

Your analysis must include:
- diagram_type: the single best Mermaid diagram type for this use case
- components: all explicit entities, actors, systems, or nodes present in the description
- missing_components: logically necessary components that are implied but not stated (e.g. error handlers, queues, databases, audit logs)
- relationships: all connections and interactions between components, with direction and action
- decision_points: all branching logic, conditions, or gateways (e.g. "Is order valid?", "Sufficient balance?")
- best_practices: architectural improvements to add for correctness, resilience, or clarity

Think rigorously. Do not hallucinate components not implied by the domain.
"""


def build_analyzer_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", ANALYZER_SYSTEM_PROMPT),
            (
                "human",
                "Analyze this diagram description:\n\n{refined_description}",
            ),
        ]
    )
