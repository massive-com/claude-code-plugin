# Testing Guide

This document is a hands-on checklist for verifying the Massive Claude Code plugin works correctly. A tester should be able to complete all sections in roughly 60-90 minutes.

## Prerequisites

Before starting, confirm the following:

- [ ] Claude Code CLI installed and working (`claude --version`)
- [ ] Python 3.12+ installed (`python3 --version`)
- [ ] [uv](https://docs.astral.sh/uv/) installed (`uv --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] Go 1.21+ installed (`go version`)
- [ ] (Optional) JDK 21+ and Gradle for Kotlin tests (`java -version`, `gradle --version`)
- [ ] A Massive API key (free Basic tier works for most tests; get one at [massive.com/dashboard](https://massive.com/dashboard))
- [ ] Git clone of this repo

### MCP server setup (required for §2, §4, §5 runtime tests)

The plugin does not bundle an MCP server. Install and register it once before the live-API sections:

```bash
# Install the server binary globally via uv
uv tool install "mcp_massive @ git+https://github.com/massive-com/mcp_massive"

# Register it with Claude Code at user scope
claude mcp add massive --scope user --env MASSIVE_API_KEY=your_key -- mcp_massive
```

- [ ] `which mcp_massive` returns a path under `~/.local/bin/`
- [ ] `claude mcp list` shows `massive` with status `✓ Connected`
- [ ] Skip this subsection if you only want to test §3 (API knowledge, no MCP)

## 1. Local plugin loading

Verify the plugin loads correctly from a local directory.

```bash
claude --plugin-dir .
```

- [ ] Claude Code starts without errors
- [ ] No warnings about missing files or invalid plugin config
- [ ] The five skills appear when you type `/massive:` (tab completion or listing)
- [ ] `/reload-plugins` shows: 1 plugins, 5 skills, 0 errors

## 2. MCP server availability

The Massive MCP server is registered at user scope (see Prerequisites), so it's available in every Claude Code session — no per-plugin wiring. If you skipped the MCP setup, the tools below won't exist and §4 tests won't apply.

**Prompt:** `What MCP tools do you have available from Massive?`

- [ ] Claude lists three tools: `search_endpoints`, `call_api`, `query_data`
- [ ] No connection errors (`claude mcp list` shows `✓ Connected`)

If the tools are missing: run `claude mcp list`. If `massive` is absent, go back to Prerequisites and run the `claude mcp add` command. If it's listed but shows an error, try `mcp_massive` in a terminal to smoke-test the binary — it should start and wait for stdin.

## 3. API knowledge (no tools needed)

These tests verify that `.claude/CLAUDE.md` is loaded and Claude knows Massive conventions.

### 3a. Ticker formats

**Prompt:** `What ticker would I use to get Bitcoin price data from Massive?`

- [ ] Claude responds with `X:BTCUSD` (not `BTCUSD` or `BTC`)
- [ ] Claude mentions the `X:` prefix is for crypto

**Prompt:** `How do I get S&P 500 index data?`

- [ ] Claude responds with `I:SPX` (not `SPX` or `^SPX`)

### 3b. SDK patterns (Python)

**Prompt:** `Show me how to get 30 days of AAPL daily bars using the Python SDK`

- [ ] Code has `load_dotenv()` BEFORE `from massive import RESTClient` (import ordering matters)
- [ ] Code uses `RESTClient()` (no hardcoded key)
- [ ] Code uses `islice()` to cap the generator
- [ ] Code uses `list_aggs("AAPL", 1, "day", ...)` with correct parameter order
- [ ] Code passes `sort="asc"` for chronological order
- [ ] Timestamps converted with `datetime.fromtimestamp(bar.timestamp / 1000)` or `pd.to_datetime(..., unit="ms")` (NOT raw strftime on bar.timestamp)

### 3c. SDK patterns (JavaScript)

**Prompt:** `I'm building a Node.js app. Show me how to get AAPL daily bars with the Massive JS SDK.`

- [ ] Code uses `import { restClient } from "@massive.com/client-js"`
- [ ] Code uses `restClient(process.env.MASSIVE_API_KEY)` (not `RESTClient()`)
- [ ] Method is `getStocksAggregates` (not `list_aggs`)
- [ ] ALL methods take a single object parameter: `getStocksAggregates({ stocksTicker: "AAPL", multiplier: 1, timespan: "day", ... })`
- [ ] Bar fields are abbreviated: `bar.o`, `bar.h`, `bar.l`, `bar.c`, `bar.v`, `bar.t`
- [ ] Timestamps converted with `new Date(bar.t)`
- [ ] No Python patterns present (`RESTClient`, `list_aggs`, `load_dotenv`)

### 3d. SDK patterns (Go)

**Prompt:** `I'm writing Go. Show me how to get AAPL daily bars with the Massive Go SDK.`

- [ ] Uses `rest.New("")` (reads from env) with `godotenv.Load()` before it
- [ ] Method is `GetStocksAggregatesWithResponse` (not `list_aggs`)
- [ ] First param is `context.Background()`
- [ ] Uses `rest.Ptr()` for optional params
- [ ] Nil-checks `resp.JSON200` and `resp.JSON200.Results` before accessing
- [ ] Bar fields: `bar.O`, `bar.H`, `bar.L`, `bar.C`, `bar.V`, `bar.Timestamp`

### 3e. SDK patterns (Kotlin)

**Prompt:** `I'm building an Android app with Kotlin. Show me how to get AAPL daily bars.`

- [ ] Uses `PolygonRestClient(apiKey)` (NOT `DefaultApi()` or `ApiClient.apiKey`)
- [ ] Package is `io.polygon.kotlin.sdk.rest` (NOT `org.openapitools.client`)
- [ ] Method is `getAggregatesBlocking(AggregatesParameters(...))` (NOT `getStocksAggregates`)
- [ ] Bar fields use full names: `bar.open`, `bar.high`, `bar.low`, `bar.close`, `bar.volume`, `bar.timestampMillis`
- [ ] Mentions JitPack dependency (`com.github.massive-com:client-jvm:v5.1.2`)

### 3f. `get_*` vs `list_*` distinction (Python)

**Prompt:** `How do I use the RSI indicator with the Massive Python SDK?`

- [ ] Claude uses `get_rsi()` (not `list_rsi`)
- [ ] Accesses result via `result.values` (NOT `list(islice(...))`)
- [ ] Explains that `get_*` methods return single objects, not iterators
- [ ] Each value has `.timestamp` and `.value`

### 3g. Pagination awareness

**Prompt:** `How does pagination work in the Massive Python SDK?`

- [ ] Claude explains that `list_` methods return generators
- [ ] Claude explains that `limit` controls page size, not total results
- [ ] Claude mentions `islice()` for capping results
- [ ] Claude does NOT tell the user to manually handle `next_url`

### 3h. Plan tier awareness

**Prompt:** `I want to get real-time stock quotes. What plan do I need?`

- [ ] Claude mentions that quotes require Advanced plan ($199/mo) or higher
- [ ] Claude distinguishes between Individual and Business plans
- [ ] Claude does NOT say quotes are available on all plans

### 3i. Gotchas

**Prompt:** `Can I stream real-time data from the REST API?`

- [ ] Claude says no, REST endpoints are polled, not streamed
- [ ] Claude points to WebSocket for real-time streaming

## 4. MCP server tools

These tests require a valid API key with at least Basic tier access.

### 4a. Endpoint search

**Prompt:** `Use the MCP tools to find endpoints for stock aggregates`

- [ ] Claude calls `search_endpoints` with a relevant query
- [ ] Results include the custom bars endpoint (`/v2/aggs/ticker/{stocksTicker}/range/...`)

### 4b. API call

**Prompt:** `Call the API to get AAPL's last 5 daily bars and store the results`

- [ ] Claude calls `call_api` with the correct endpoint and parameters
- [ ] Claude uses `store_as` to save results as a DataFrame
- [ ] Results contain OHLCV data for AAPL

### 4c. SQL query

**Prompt:** `Query the stored data to show me the day with the highest volume`

- [ ] Claude calls `query_data` with a SQL statement against the stored DataFrame
- [ ] Returns a single row with the highest volume day

## 5. Skills

### 5a. Scaffold - Python REST (`/massive:scaffold`)

**Prompt:** `/massive:scaffold test-project rest python`

- [ ] Creates a `test-project/` directory
- [ ] Contains `pyproject.toml` with `massive>=2.4.0` and `python-dotenv`
- [ ] Contains `.env.example` with `MASSIVE_API_KEY=your_api_key_here`
- [ ] Contains `.gitignore` with `.env` excluded
- [ ] Contains `main.py` with `load_dotenv()` BEFORE `from massive import RESTClient`
- [ ] Contains `README.md` with quickstart (cd, cp .env.example, uv sync, uv run)
- [ ] Claude mentions which plan tier the project needs
- [ ] Claude points to `/massive:discover` and `/massive:debug` as follow-ups
- [ ] **Runtime test:** `cd test-project && cp .env.example .env`, add key, `uv sync && uv run python main.py` produces real data

### 5b. Scaffold - JavaScript REST

**Prompt:** `/massive:scaffold test-js rest javascript`

- [ ] Creates `package.json` with `"@massive.com/client-js": "^10.6.0"` (pinned, NOT `"latest"`) and `dotenv`, `"type": "module"`
- [ ] Creates `index.js` using `restClient()`, `getStocksAggregates({...})` with object params
- [ ] Bar fields are abbreviated (`bar.o`, `bar.h`, etc.)
- [ ] No Python patterns (`RESTClient`, `list_aggs`, `load_dotenv`)
- [ ] **Runtime test:** `npm install && node index.js` produces real data

### 5c. Scaffold - Go REST

**Prompt:** `/massive:scaffold test-go rest go`

- [ ] Creates `go.mod` with `github.com/massive-com/client-go/v3` and `godotenv`
- [ ] Creates `main.go` with `GetStocksAggregatesWithResponse`, `rest.Ptr()`, nil checks
- [ ] No Python patterns
- [ ] **Runtime test:** `go mod tidy && go run main.go` produces real data

### 5d. Scaffold - Kotlin REST

**Prompt:** `/massive:scaffold test-kt rest kotlin`

- [ ] Creates `build.gradle.kts` with `com.github.massive-com:client-jvm:v5.1.2` from JitPack
- [ ] Creates `src/main/kotlin/Main.kt` with `PolygonRestClient(apiKey)`, `getAggregatesBlocking(AggregatesParameters(...))`
- [ ] Bar fields are full names (`bar.open`, `bar.high`, `bar.timestampMillis`)
- [ ] No Python/JS patterns
- [ ] **Runtime test** (requires JDK): `gradle wrapper && ./gradlew run` produces real data

### 5e. Scaffold - WebSocket (all languages)

**Prompt:** `/massive:scaffold ws-py websocket python`

- [ ] **Plan tier warning:** Claude flags that WebSocket requires Starter plan ($29-49/mo) or above BEFORE scaffolding, or confirms the user has Starter
- [ ] Imports `from massive.websocket.models import Market, Feed`
- [ ] Uses `WebSocketClient(api_key=..., market=Market.Stocks, subscriptions=[...])`
- [ ] Has handler function and `client.run(handle_msg=handler)`

**Prompt:** `/massive:scaffold ws-js websocket javascript`

- [ ] Uses `websocketClient()` and `ws.stocks()` (not Python's `WebSocketClient`)
- [ ] Uses `JSON.stringify({ action: "subscribe", params: "T.AAPL" })`

**Prompt:** `/massive:scaffold ws-go websocket go`

- [ ] Uses `massivews.New(massivews.Config{...})` with channel-based `c.Output()`

**Prompt:** `/massive:scaffold ws-kt websocket kotlin`

- [ ] Uses `PolygonWebSocketClient` with listener pattern, subscribes after `onAuthenticated`

### 5f. Discover (`/massive:discover`)

**Prompt (with JS context):** `I'm building a Node.js app. /massive:discover "options Greeks for SPY"`

- [ ] Shows JavaScript SDK example (not Python)
- [ ] Uses `getOptionsChain({underlyingAsset: "SPY", ...})` with object params
- [ ] Mentions plan tier requirements (Options Starter or above)

**Prompt (no language context):** `/massive:discover "treasury yield curve data"`

- [ ] Defaults to Python example
- [ ] Includes `load_dotenv()` before import

### 5g. Debug (`/massive:debug`)

**Python error:**
**Prompt:** `/massive:debug TypeError: 'SingleIndicatorResults' object is not iterable when running: rsi = list(client.get_rsi('AAPL', params={'window': 14}))`

- [ ] Identifies `get_rsi()` returns `SingleIndicatorResults`, not an iterator
- [ ] Suggests `result.values` pattern
- [ ] Explains `get_*` vs `list_*` distinction

**JavaScript error:**
**Prompt:** `/massive:debug I get 'client.list_aggs is not a function' in my Node.js code`

- [ ] Identifies `list_aggs` as the Python method name
- [ ] Suggests `getStocksAggregates({stocksTicker: ...})` with object params
- [ ] Fix is in JavaScript, not Python

**Go error:**
**Prompt:** `/massive:debug My Go code panics with nil pointer dereference on resp.JSON200.Results`

- [ ] Suggests nil-check guard: `if resp.JSON200 != nil && resp.JSON200.Results != nil`
- [ ] Fix is in Go

**Kotlin error:**
**Prompt:** `/massive:debug Could not resolve com.github.massive-com:client-jvm:v5.1.2 in Gradle`

- [ ] Identifies missing JitPack repository
- [ ] Suggests adding `maven("https://jitpack.io")` to repositories

**Rate-limit error (Python):**
**Prompt:** `/massive:debug I keep getting BadResponse errors with "You've exceeded the maximum requests per minute" during a batch job`

- [ ] Identifies as a 429 rate-limit (Basic tier: 5 calls/min)
- [ ] Provides `with_backoff` helper using body-text markers (`"maximum requests"`, `"rate limit"`, `"too many requests"`) NOT `"429" in str(e)` (the SDK body does not include HTTP status)
- [ ] Suggests caching, universal snapshot batching, or upgrading to Starter

**Rate-limit retry (JS/Go):**
**Prompt:** `/massive:debug how do I retry 429s in my Node.js / Go code?`

- [ ] JS example uses `err?.status ?? err?.response?.status === 429` (axios error shape)
- [ ] Go example uses `strings.Contains(err.Error(), "429")` (SDK includes HTTP status in error)

**Go Last Trade fields:**
**Prompt:** `/massive:debug In Go, resp.JSON200.Results.P is undefined after GetLastStocksTradeWithResponse`

- [ ] Identifies that the generated struct names the trade price `BidPrice` and size `BidSize` (JSON-tagged `p` and `s`), despite being on a Trade response
- [ ] Suggests using `r.BidPrice` and `r.BidSize` (nil-check `*float64`)

### 5h. Options (`/massive:options`)

**Prompt:** `/massive:options "bull call spread" SPY python`

- [ ] **Plan tier check:** Claude asks about or confirms Options Starter ($49/mo) BEFORE scaffolding (since Greeks/IV are gated)
- [ ] Creates a project DIRECTORY (not a throwaway script)
- [ ] `pyproject.toml` has `massive>=2.4.0` (NOT `massive-sdk`)
- [ ] `main.py` has `load_dotenv()` before `from massive import RESTClient`
- [ ] **Dynamic expiration dates:** Expiration window is derived from `date.today()` (e.g., `today + timedelta(days=7)` to `today + timedelta(days=60)`), NOT hardcoded past dates like `"2025-06-01"`
- [ ] Includes `.env.example`, `.gitignore`, `README.md` with plan-tier note
- [ ] Quickstart output: cd, cp .env.example, install, run
- [ ] Calculates max profit, max loss, breakeven, risk/reward

**Prompt:** `/massive:options "covered call" AAPL javascript`

- [ ] Creates project with `package.json` (pins `"@massive.com/client-js": "^10.6.0"`)
- [ ] Uses `getOptionsChain({underlyingAsset: ...})` with object params
- [ ] Notes Options Starter plan requirement upfront (not just at the end)

### 5i. Dashboard (`/massive:dashboard`)

**Prompt:** `/massive:dashboard test-dash multi-asset`

- [ ] Creates modular project structure with `terminal/` subdirectory
- [ ] `data.py`: technical indicators use `result.values` pattern (NOT `list(islice(...))`)
- [ ] `data.py`: market status uses `client.get_market_status()` SDK method (NOT raw REST)
- [ ] `data.py`: `list_aggs` passes `sort="asc"`
- [ ] No `requests` library in dependencies or code
- [ ] Quickstart: cd, cp .env.example .env, uv sync, uv run streamlit run

**Prompt:** `/massive:dashboard macro-dash macro`

- [ ] Uses SDK methods: `list_treasury_yields()`, `list_inflation()`, `list_labor_market_indicators()`
- [ ] Does NOT use `requests.get` or raw HTTP calls
- [ ] No references to any API domain other than `api.massive.com`

Clean up test directories after each test.

## 6. Cross-tool files

Cross-tool instruction files (Cursor, Copilot, Gemini, Windsurf, and others) have been moved to the standalone [massive-ai-rules](https://github.com/massive-com/massive-ai-rules) repo. Test them there.

## 7. Brand and terminology

Review all Claude responses from the tests above and verify:

- [ ] REST endpoints described as "polled," never "streamed"
- [ ] Individual tickers not called "markets" (markets = asset classes)
- [ ] No claim that one endpoint covers all asset classes
- [ ] No emojis in any output (including Streamlit `page_icon`)
- [ ] No em dashes in any output (use commas, periods, semicolons, parentheses)
- [ ] No mention of "stock data app" (should be "financial dashboard," "quantitative analysis," etc.)
- [ ] No references to "polygon.io" in any generated code or output
- [ ] All API URLs use `api.massive.com`
- [ ] Package name is `massive` (never `massive-sdk`, `massive-api`)

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

### 8d. Plan-tier guardrails (new)

**Prompt:** `/massive:scaffold live-tape websocket python` (tester on free Basic plan)

- [ ] Claude stops before scaffolding and asks whether the user has Starter or above
- [ ] If tester confirms "no, Basic": Claude either scaffolds with a clear plan-tier note in the README or suggests a `rest` project instead
- [ ] If tester confirms "yes, Starter+": Claude proceeds to scaffold normally

**Prompt:** `/massive:options "iron condor" SPY python` (tester on free Basic Options plan)

- [ ] Claude stops and asks about Options Starter access before scaffolding
- [ ] If Basic Options: Claude offers a degraded version (open-interest/volume/strike filtering, no Greek-based ranking)
- [ ] If Options Starter+: Claude proceeds with full Greeks-based strategy

### 8e. README troubleshooting references (new)

**Prompt:** `The MCP server is not starting, what do I check?`

- [ ] Claude references the README Troubleshooting section
- [ ] Mentions `uv --version`, Python 3.12+ requirement, `claude --debug` for logs
- [ ] Does NOT fabricate a workaround that bypasses uvx

**Prompt:** `How do I verify my plugin setup is working?`

- [ ] Claude points to the 3-step verify-setup checklist in README (plugin loaded, MCP running, API key working)

## Test results

| Section | Pass/Fail | Notes |
|---|---|---|
| 1. Plugin loading | | |
| 2. MCP server startup | | |
| 3a. Ticker formats | | |
| 3b. Python SDK patterns | | |
| 3c. JS SDK patterns | | |
| 3d. Go SDK patterns | | |
| 3e. Kotlin SDK patterns | | |
| 3f. get_* vs list_* | | |
| 3g. Pagination | | |
| 3h. Plan tiers | | |
| 3i. Gotchas | | |
| 4a. Endpoint search | | |
| 4b. API call | | |
| 4c. SQL query | | |
| 5a. Scaffold Python REST | | |
| 5b. Scaffold JS REST | | |
| 5c. Scaffold Go REST | | |
| 5d. Scaffold Kotlin REST | | |
| 5e. Scaffold WebSocket (all) | | |
| 5f. Discover (multi-lang) | | |
| 5g. Debug (multi-lang) | | |
| 5h. Options (multi-lang) | | |
| 5i. Dashboard (all focus) | | |
| 7. Brand/terminology | | |
| 8a. No API key | | |
| 8b. Mixed-asset snapshot | | |
| 8c. Futures awareness | | |
| 8d. Plan-tier guardrails | | |
| 8e. README troubleshooting | | |
