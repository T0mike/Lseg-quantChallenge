from __future__ import annotations

from langchain.chat_models import init_chat_model

from .config import MermaidAgentSettings
from .exceptions import MermaidConfigurationError


def create_chat_model(settings: MermaidAgentSettings):
    try:
        return init_chat_model(
            model=settings.model_name,
            model_provider=settings.model_provider,
            temperature=settings.temperature,
        )
    except Exception as exc:
        raise MermaidConfigurationError(
            "Unable to initialize the LangChain chat model. "
            "Check the provider package and required API credentials."
        ) from exc
