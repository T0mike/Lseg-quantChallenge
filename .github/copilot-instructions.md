# Repository Structure

This project generates Mermaid diagrams from natural language descriptions.
It is built as a multi-stage LLM processing pipeline using LangChain and Streamlit.

## Architecture

The application is a **Streamlit web app** (`main.py`) that orchestrates a chain
of processing modules living under `src/`. Each module is a self-contained
pipeline stage with its own LLM configuration, prompts, and logic.

```
User input → [preprocessing] → [analysis] → [generation] → [enhancement] → Mermaid diagram
```

### Processing pipeline

1. **Preprocessing** (`src/preprocessing/`) — Takes raw, potentially vague or
   non-English user input and rewrites it into a clear, precise English
   description optimized for Mermaid diagram generation.

2. **Analysis** (`src/analysis/`) — Examines the optimized description and
   produces a structured architectural analysis (diagram type, components,
   relationships, decision points, best practices) that guides generation.

3. **Generation** (`src/generation/`) — Converts the optimized description and
   analysis into valid Mermaid syntax. Handles code-fence stripping,
   diagram-type detection, validation, and Streamlit rendering.

4. **Enhancement** (`src/enhancement/`) — Post-generation step that suggests
   AI-powered improvements to the diagram. Presents suggestions in an
   interactive UI where the user can preview and accept individual changes.
   Accepted suggestions are merged into the diagram reactively.

### Module conventions

Every module under `src/` follows the same structure:

| File | Role |
|------|------|
| `__init__.py` | Public API exports |
| `config.py` | Dataclass settings loaded from environment variables |
| `prompts.py` | LangChain `ChatPromptTemplate` definitions |
| `agent.py`, `optimizer.py`, or `enhancer.py` | Core logic class that wires prompt → model → parser |
| `models.py` | `init_chat_model()` wrapper with error handling (if present) |
| `schemas.py` | Pydantic models for structured LLM output (if present) |
| `exceptions.py` | Module-specific exception hierarchy (if present) |

### Key files

| Path | Purpose |
|------|---------|
| `main.py` | Streamlit entry point; wires preprocessing → analysis → generation → enhancement |
| `pyproject.toml` | Dependencies and project metadata |
| `data/initial.txt` | Sample input for testing |
| `.streamlit/secrets.toml` | Local API keys (not committed) |

### LLM providers

Models are configured per-module via environment variables. The project uses
LangChain's `init_chat_model()` abstraction, supporting any provider with a
`langchain-<provider>` integration package installed. Current dependencies
include `langchain-anthropic` and `langchain-openai`.
