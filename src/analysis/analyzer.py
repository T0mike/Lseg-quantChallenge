from __future__ import annotations

import os
from dataclasses import dataclass

from langchain.chat_models import init_chat_model

from .prompts import build_analyzer_prompt
from .schemas import DiagramAnalysis


@dataclass
class DiagramAnalyzer:
    model_name: str = "claude-haiku-4-5-20251001"
    model_provider: str = "anthropic"

    def __post_init__(self) -> None:
        model = init_chat_model(
            model=self.model_name,
            model_provider=self.model_provider,
            temperature=0.0,
        )
        self._chain = build_analyzer_prompt() | model.with_structured_output(DiagramAnalysis)

    @classmethod
    def from_env(cls) -> "DiagramAnalyzer":
        return cls(
            model_name=os.getenv("ANALYZER_MODEL", cls.model_name),
            model_provider=os.getenv("ANALYZER_PROVIDER", cls.model_provider),
        )

    def analyze(self, refined_description: str) -> DiagramAnalysis:
        return self._chain.invoke({"refined_description": refined_description})
