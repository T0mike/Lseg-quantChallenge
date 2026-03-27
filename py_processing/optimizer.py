from __future__ import annotations

from dataclasses import dataclass

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser

from .prompts import build_optimizer_prompt


@dataclass
class PromptOptimizer:
    model_name: str = "claude-haiku-4-5-20251001"
    model_provider: str = "anthropic"

    def __post_init__(self) -> None:
        model = init_chat_model(
            model=self.model_name,
            model_provider=self.model_provider,
            temperature=0.0,
        )
        self._chain = build_optimizer_prompt() | model | StrOutputParser()

    @classmethod
    def from_env(cls) -> "PromptOptimizer":
        import os
        return cls(
            model_name=os.getenv("OPTIMIZER_MODEL", cls.model_name),
            model_provider=os.getenv("OPTIMIZER_PROVIDER", cls.model_provider),
        )

    def optimize(self, raw_input: str) -> str:
        return self._chain.invoke({"raw_input": raw_input})

    def stream_optimize(self, raw_input: str):
        for chunk in self._chain.stream({"raw_input": raw_input}):
            yield chunk
