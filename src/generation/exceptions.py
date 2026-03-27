class MermaidAgentError(Exception):
    """Base exception for Mermaid agent failures."""


class MermaidConfigurationError(MermaidAgentError):
    """Raised when the LLM provider is not configured correctly."""


class MermaidValidationError(MermaidAgentError):
    """Raised when the generated Mermaid diagram is invalid."""
