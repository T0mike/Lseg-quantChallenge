from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MermaidAgentSettings:
    model_name: str = "gpt-5.4"
    model_provider: str = "openai"
    temperature: float = 0.0

    @classmethod
    def from_env(cls) -> "MermaidAgentSettings":
        return cls(
            model_name=os.getenv("MERMAID_AGENT_MODEL", cls.model_name),
            model_provider=os.getenv(
                "MERMAID_AGENT_PROVIDER",
                cls.model_provider,
            ),
            temperature=float(
                os.getenv("MERMAID_AGENT_TEMPERATURE", str(cls.temperature)),
            ),
        )
