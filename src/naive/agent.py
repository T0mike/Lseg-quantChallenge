from __future__ import annotations

from dataclasses import dataclass

from langchain_core.output_parsers import StrOutputParser

from .config import MermaidAgentSettings
from .mermaid import normalize_mermaid
from .models import create_chat_model
from .prompts import build_mermaid_prompt


@dataclass
class MermaidAgent:
    settings: MermaidAgentSettings

    def __post_init__(self) -> None:
        prompt = build_mermaid_prompt()
        model = create_chat_model(self.settings)
        self._chain = prompt | model | StrOutputParser()

    @classmethod
    def from_env(cls) -> "MermaidAgent":
        return cls(settings=MermaidAgentSettings.from_env())

    def generate_diagram(self, description: str) -> str:
        diagram = self._chain.invoke({"description": description})
        return normalize_mermaid(diagram)

    def stream_diagram(self, description: str):
        for chunk in self._chain.stream({"description": description}):
            yield chunk
