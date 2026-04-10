# Testing Guide

This document is a hands-on checklist for verifying the Massive Claude Code plugin works correctly. A tester should be able to complete all sections in roughly 30-45 minutes.

## Prerequisites

Before starting, confirm the following:

- [ ] Claude Code CLI installed and working (`claude --version`)
- [ ] Python 3.12+ installed (`python3 --version`)
- [ ] [uv](https://docs.astral.sh/uv/) installed (`uv --version`)
- [ ] A Massive API key (free Basic tier works for most tests; get one at [massive.com/dashboard](https://massive.com/dashboard))
- [ ] Git clone of this repo

## 1. Local plugin loading

Verify the plugin loads correctly from a local directory.

```bash
claude --plugin-dir .
```

- [ ] Claude Code starts without errors
- [ ] No warnings about missing files or invalid plugin config
- [ ] The five skills appear when you type `/massive:` (tab completion or listing)

## 2. MCP server startup

The Massive MCP server should start automatically when the plugin loads.

**Prompt:** `What MCP tools do you have available from Massive?`

- [ ] Claude lists four tools: `search_endpoints`, `get_endpoint_docs`, `call_api`, `query_data`
- [ ] No errors about the MCP server failing to start

If the MCP server fails to start, check:
- Python 3.12+ is available on PATH
- `uvx` is available (comes with uv)
- Your API key was entered correctly during plugin setup

## 3. API knowledge (no tools needed)

These tests verify that `.claude/CLAUDE.md` is loaded and Claude knows Massive conventions without being told.

### 3a. Ticker formats

**Prompt:** `What ticker would I use to get Bitcoin price data from Massive?`

- [ ] Claude responds with `X:BTCUSD` (not `BTCUSD` or `BTC`)
- [ ] Claude mentions the `X:` prefix is for crypto

**Prompt:** `How do I get S&P 500 index data?`

- [ ] Claude responds with `I:SPX` (not `SPX` or `^SPX`)

### 3b. SDK patterns

**Prompt:** `Show me how to get 30 days of AAPL daily bars using the Python SDK`

- [ ] Code uses `from massive import RESTClient`
- [ ] Code uses `load_dotenv()` and `RESTClient()` (no hardcoded key)
- [ ] Code uses `islice()` to cap the generator
- [ ] Code uses `list_aggs("AAPL", 1, "day", ...)` with correct parameter order
- [ ] Code passes `sort="asc"` for chronological order

### 3c. Pagination awareness

**Prompt:** `How does pagination work in the Massive Python SDK?`

- [ ] Claude explains that `list_` methods return generators
- [ ] Claude explains that `limit` controls page size, not total results
- [ ] Claude mentions `islice()` for capping results
- [ ] Claude does NOT tell the user to manually handle `next_url`

### 3d. Plan tier awareness

**Prompt:** `I want to get real-time stock quotes. What plan do I need?`

- [ ] Claude mentions that quotes require Advanced plan ($199/mo) or higher
- [ ] Claude distinguishes between Individual and Business plans
- [ ] Claude does NOT say quotes are available on all plans

### 3e. Gotchas

**Prompt:** `Can I stream real-time data from the REST API?`

- [ ] Claude says no, REST endpoints are polled, not streamed
- [ ] Claude points to WebSocket for real-time streaming

## 4. MCP server tools

These tests require a valid API key with at least Basic tier access.

### 4a. Endpoint search

**Prompt:** `Use the MCP tools to find endpoints for stock aggregates`

- [ ] Claude calls `search_endpoints` with a relevant query
- [ ] Results include the custom bars endpoint (`/v2/aggs/ticker/{stocksTicker}/range/...`)

### 4b. Endpoint documentation

**Prompt:** `Get me the full documentation for the stock aggregates custom bars endpoint`

- [ ] Claude calls `get_endpoint_docs` with the docs URL from search results
- [ ] Response includes parameter descriptions (ticker, multiplier, timespan, from, to, adjusted, sort, limit)

### 4c. API call

**Prompt:** `Call the API to get AAPL's last 5 daily bars and store the results`

- [ ] Claude calls `call_api` with the correct endpoint and parameters
- [ ] Claude uses `store_as` to save results as a DataFrame
- [ ] Results contain OHLCV data for AAPL

### 4d. SQL query

**Prompt:** `Query the stored data to show me the day with the highest volume`

- [ ] Claude calls `query_data` with a SQL statement against the stored DataFrame
- [ ] Returns a single row with the highest volume day

## 5. Skills

### 5a. Scaffold (`/massive:scaffold`)

**Prompt:** `/massive:scaffold test-project rest`

- [ ] Creates a `test-project/` directory
- [ ] Contains `pyproject.toml` with `massive>=2.4.0` and `python-dotenv`
- [ ] Contains `.env.example` with `MASSIVE_API_KEY=your_api_key_here`
- [ ] Contains `.gitignore` with `.env` excluded
- [ ] Contains `main.py` with `RESTClient()`, `load_dotenv()`, and a sample `list_aggs` call
- [ ] Contains `README.md` with quickstart instructions
- [ ] Claude mentions which plan tier the project needs

**Prompt:** `/massive:scaffold ws-demo websocket`

- [ ] Creates a project with WebSocket boilerplate
- [ ] Code imports `Market` from `massive.websocket.models`
- [ ] Code uses `WebSocketClient(api_key=..., market=Market.Stocks, subscriptions=[...])`

**Prompt:** `/massive:scaffold dash-demo streamlit`

- [ ] Creates a project with Streamlit boilerplate
- [ ] Includes `streamlit` and `plotly` in dependencies
- [ ] Uses `@st.cache_resource` for client singleton
- [ ] Uses `@st.cache_data(ttl=...)` for API call caching

Clean up test directories after each test.

### 5b. Discover (`/massive:discover`)

**Prompt:** `/massive:discover "options Greeks for SPY"`

- [ ] Claude searches for endpoints using MCP `search_endpoints`
- [ ] Finds the options chain snapshot endpoint
- [ ] Shows the endpoint URL, key parameters, and a Python SDK example
- [ ] Mentions plan tier requirements (Options Starter or above for Greeks/IV)
- [ ] Uses correct ticker format in examples

**Prompt:** `/massive:discover "treasury yield curve data"`

- [ ] Finds the `/fed/v1/treasury-yields` endpoint
- [ ] Shows available yield fields (1mo through 30yr)

### 5c. Debug (`/massive:debug`)

Set up a test file with a deliberate error, then run the skill.

**Create `buggy.py`:**
```python
from massive import RESTClient
client = RESTClient()
trades = client.list_trades("BTCUSD")  # wrong: missing X: prefix
for t in trades:
    print(t)
```

**Prompt:** `/massive:debug` (with `buggy.py` in the working directory)

- [ ] Claude reads the code and identifies the ticker format issue
- [ ] Suggests changing `BTCUSD` to `X:BTCUSD`
- [ ] Explains the crypto prefix convention

**Prompt:** `I'm getting HTTP 403 when trying to access the options chain. I'm on the Basic plan.`

- [ ] Claude explains that options chain data needs at least Starter plan
- [ ] Mentions the specific pricing ($29/mo for Options Starter)
- [ ] Does NOT tell the user to just retry or check their key

### 5d. Options (`/massive:options`)

**Prompt:** `/massive:options "covered call" AAPL`

- [ ] Claude fetches the current AAPL price
- [ ] Fetches the options chain using `list_snapshot_options_chain`
- [ ] Filters for OTM calls with appropriate delta range
- [ ] Shows risk/reward metrics (premium, annualized return, breakeven)
- [ ] Generates reusable Python code
- [ ] Uses correct OCC symbology format (`O:AAPL...`)

### 5e. Dashboard (`/massive:dashboard`)

**Prompt:** `/massive:dashboard test-dash multi-asset`

- [ ] Creates a modular project structure with `terminal/` subdirectory
- [ ] Includes `data.py`, `config.py`, `charts.py`, and panel modules
- [ ] Uses `@st.cache_resource` for client singleton
- [ ] Uses TTL-based caching with reasonable defaults
- [ ] Includes `.streamlit/config.toml` with dark theme
- [ ] Uses `list_universal_snapshots(ticker_any_of=[...])` with correct calling convention
- [ ] Uses Plotly with dark theme

Clean up test directory after.

## 6. Cross-tool files

### 6a. Cursor

- [ ] Open a project in Cursor
- [ ] Copy `cross-tool/.cursorrules` to `.cursor/rules/massive.mdc`
- [ ] Ask Cursor: "Show me how to get AAPL daily bars with the Massive SDK"
- [ ] Verify it uses correct imports, `RESTClient()`, `islice()`, and `sort="asc"`

### 6b. GitHub Copilot

- [ ] Copy `cross-tool/copilot-instructions.md` to `.github/copilot-instructions.md`
- [ ] Ask Copilot a similar question
- [ ] Verify it follows the same conventions

## 7. Brand and terminology

Review all Claude responses from the tests above and verify:

- [ ] REST endpoints described as "polled," never "streamed"
- [ ] Individual tickers not called "markets" (markets = asset classes)
- [ ] No claim that one endpoint covers all asset classes
- [ ] No emojis in any output
- [ ] No em dashes in any output
- [ ] No mention of "stock data app" (should be "financial dashboard," "quantitative analysis," etc.)

## 8. Edge cases

### 8a. No API key

**Prompt:** (start Claude Code without providing an API key during plugin setup)

- [ ] Claude can still answer API knowledge questions from `.claude/CLAUDE.md`
- [ ] MCP tool calls fail gracefully with a clear auth error
- [ ] Claude suggests checking `MASSIVE_API_KEY` in `.env` or the dashboard

### 8b. Mixed-asset snapshot

**Prompt:** `Get me a snapshot of AAPL, Bitcoin, Euro/USD, and the S&P 500 in a single call`

- [ ] Claude uses `list_universal_snapshots(ticker_any_of=["AAPL", "X:BTCUSD", "C:EURUSD", "I:SPX"])`
- [ ] Does NOT make four separate API calls

### 8c. Futures awareness

**Prompt:** `How do I get futures aggregates for the E-mini S&P 500?`

- [ ] Claude uses the correct futures endpoint path (`/futures/vX/aggs/{ticker}`)
- [ ] Does NOT use the equity aggregates endpoint
- [ ] Mentions the correct ticker format (e.g., `ESM6` for a contract, or `ES` for the product)

## Test results

| Section | Pass/Fail | Notes |
|---|---|---|
| 1. Plugin loading | | |
| 2. MCP server startup | | |
| 3a. Ticker formats | | |
| 3b. SDK patterns | | |
| 3c. Pagination | | |
| 3d. Plan tiers | | |
| 3e. Gotchas | | |
| 4a. Endpoint search | | |
| 4b. Endpoint docs | | |
| 4c. API call | | |
| 4d. SQL query | | |
| 5a. Scaffold | | |
| 5b. Discover | | |
| 5c. Debug | | |
| 5d. Options | | |
| 5e. Dashboard | | |
| 6a. Cursor | | |
| 6b. Copilot | | |
| 7. Brand/terminology | | |
| 8a. No API key | | |
| 8b. Mixed-asset snapshot | | |
| 8c. Futures awareness | | |
