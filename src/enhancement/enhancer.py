from __future__ import annotations

import json
from dataclasses import dataclass

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from .config import EnhancementSettings
from .prompts import build_suggest_prompt, build_apply_prompt, build_freeform_prompt
from .schemas import EnhancementResponse, Suggestion


@dataclass
class DiagramEnhancer:
    settings: EnhancementSettings

    def __post_init__(self) -> None:
        model = init_chat_model(
            model=self.settings.model_name,
            model_provider=self.settings.model_provider,
            temperature=self.settings.temperature,
        )
        self._suggest_chain = (
            build_suggest_prompt() | model | JsonOutputParser()
        )
        self._apply_chain = (
            build_apply_prompt() | model | StrOutputParser()
        )
        self._freeform_chain = (
            build_freeform_prompt() | model | StrOutputParser()
        )

    @classmethod
    def from_env(cls) -> "DiagramEnhancer":
        return cls(settings=EnhancementSettings.from_env())

    def suggest(self, diagram: str, description: str) -> list[Suggestion]:
        raw = self._suggest_chain.invoke(
            {
                "diagram": diagram,
                "description": description,
                "max_suggestions": str(self.settings.max_suggestions),
            }
        )
        parsed = EnhancementResponse.model_validate(raw)
        return parsed.suggestions

    def apply_suggestions(
        self, diagram: str, accepted: list[Suggestion]
    ) -> str:
        accepted_text = "\n\n".join(
            f"### {s.title}\n{s.description}\n```\n{s.updated_diagram}\n```"
            for s in accepted
        )
        result = self._apply_chain.invoke(
            {
                "diagram": diagram,
                "accepted_suggestions": accepted_text,
            }
        )
        # Strip code fences if the model wraps them
        stripped = result.strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        return stripped

    @staticmethod
    def _strip_fences(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        return stripped

    def freeform_edit(self, diagram: str, instruction: str) -> str:
        result = self._freeform_chain.invoke(
            {"diagram": diagram, "instruction": instruction}
        )
        return self._strip_fences(result)
