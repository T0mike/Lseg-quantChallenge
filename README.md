# LSEG Quant Challenge

Minimal Streamlit setup.

## Run

```bash
uv run streamlit run main.py
```

## Configuration

For local Streamlit runs, put secrets in `.streamlit/secrets.toml`.

```bash
mkdir -p .streamlit
```

Example:

```toml
OPENAI_API_KEY = "your_api_key"
ANTHROPIC_API_KEY = "your_api_key"
MERMAID_AGENT_PROVIDER = "openai"
MERMAID_AGENT_MODEL = "gpt-4.1-mini"
MERMAID_AGENT_TEMPERATURE = "0"
```

When you run `uv run streamlit run main.py`, Streamlit loads root-level secrets from
`.streamlit/secrets.toml` and makes them available as environment variables for the app.
