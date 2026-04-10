---
name: scaffold
description: Scaffold a new Massive API project with pyproject.toml, .env setup, and boilerplate code. Use when creating a new project, demo, or example that uses Massive's financial data APIs.
argument-hint: "[project-name] [type: rest|websocket|streamlit]"
disable-model-invocation: false
allowed-tools: Write Edit Bash
---

# Scaffold a new Massive project

Create a new project called `$0` of type `$1` (default: `rest` if not specified).

## Project types

**rest** (default): CLI script using RESTClient for data fetching and analysis.
**websocket**: Real-time streaming script using WebSocketClient with a handler callback.
**streamlit**: Interactive dashboard using Streamlit with Plotly charts and cached API calls.

## Required files

### pyproject.toml

```toml
[project]
name = "$0"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "massive>=2.4.0",
    "python-dotenv>=1.0.0",
]
```

For **streamlit** type, add:
```toml
    "streamlit>=1.41.0",
    "plotly>=5.24.0",
    "pandas>=2.2.0",
```

### .env.example

```
MASSIVE_API_KEY=your_api_key_here
```

### .gitignore

```
.env
.venv/
__pycache__/
data/
.uv/
uv.lock
```

### main.py (rest type)

Basic structure:
1. `load_dotenv()` at top
2. `client = RESTClient()` (reads MASSIVE_API_KEY from env)
3. A sample `list_aggs()` call with `islice()` for pagination
4. Print results in a readable format

### main.py (websocket type)

Basic structure:
1. `load_dotenv()` at top
2. `WebSocketClient(api_key=key, market=Market.Stocks, subscriptions=["T.AAPL"])`
3. A handler function that processes incoming messages
4. `client.run(handle_msg=handler)`

### streamlit_app.py (streamlit type)

Basic structure:
1. `load_dotenv()` at top
2. `@st.cache_resource` for client singleton
3. `@st.cache_data(ttl=30)` for API call wrappers
4. Sidebar for ticker input
5. A price chart using Plotly with `list_aggs()` data
6. Run with `uv run streamlit run streamlit_app.py`

### README.md

Include:
1. One-line description of what the project does
2. Quickstart: `cp .env.example .env`, add your key, `uv sync`, `uv run python main.py`
3. Link to Massive docs: https://massive.com/docs

## Plan guidance

After scaffolding, remind the user which plan tier they will need:
- **Basic (free):** Enough for testing with end-of-day aggregates, reference data, technical indicators. Limited to 5 calls/min.
- **Starter ($29-49/mo):** Required for WebSocket streaming, snapshots, flat files, and second aggregates. Options Starter adds Greeks/IV.
- **Developer ($79/mo):** Required for trade data access.
- **Advanced ($99-199/mo):** Required for real-time data, quotes, and financials/ratios (Stocks Advanced).
- **Business ($999+/mo):** Required for commercial use, building products, or redistributing data.

For WebSocket and Streamlit project types, the user will need at least a Starter plan.

## Steps

1. Create the project directory: `$0/`
2. Write all files listed above
3. Confirm the structure and note the minimum plan tier needed for the project type
