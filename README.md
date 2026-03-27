# LSEG Quant Challenge

Minimal Streamlit setup.

## Run

```bash
uv run streamlit run main.py
```

## Configuration

Set an API key for your LangChain provider before running the app.

OpenAI example:

```bash
export OPENAI_API_KEY=your_api_key
uv run streamlit run main.py
```

Optional overrides:

```bash
export MERMAID_AGENT_PROVIDER=openai
export MERMAID_AGENT_MODEL=gpt-4.1-mini
export MERMAID_AGENT_TEMPERATURE=0
```
