from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class EnhancementSettings:
    model_name: str = "gpt-5.4"
    model_provider: str = "openai"
    temperature: float = 0.0
    max_suggestions: int = 5

    @classmethod
    def from_env(cls) -> "EnhancementSettings":
        return cls(
            model_name=os.getenv("ENHANCEMENT_MODEL", cls.model_name),
            model_provider=os.getenv(
                "ENHANCEMENT_PROVIDER", cls.model_provider
            ),
            temperature=float(
                os.getenv("ENHANCEMENT_TEMPERATURE", str(cls.temperature)),
            ),
            max_suggestions=int(
                os.getenv(
                    "ENHANCEMENT_MAX_SUGGESTIONS", str(cls.max_suggestions)
                ),
            ),
        )
