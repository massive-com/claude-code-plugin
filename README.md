<img src="images/logo_new.png" alt="Massive" width="100%"/>

# Massive Claude Code Plugin

Ship code against the [Massive](https://massive.com) API faster, with fewer hallucinations. This plugin loads Massive's SDK conventions, endpoint catalog, and common failure modes into every Claude Code session, plus five slash commands for the workflows you run most often.

## Why

Two problems Claude runs into when you're coding against a real financial data API.

**Slow.** Every session starts with you explaining that Bitcoin is `X:BTCUSD`, that `list_aggs` auto-paginates, that `get_rsi` returns a single object not an iterator, that crypto endpoints use a different prefix from forex. Minutes burned before any code lands.

**Wrong.** Claude is confident. It will write `list_rsi(...)` when the method is `get_rsi`, pass `tickerAnyOf` as an array in JS when the SDK wants a comma-separated string, or reach for `bar.Open` in Go when the actual field is `bar.O`. You end up debugging hallucinations instead of business logic.

This plugin fixes both. `CLAUDE.md` teaches the model the right patterns so correct code comes out the first try; the skills wrap the workflows you run most; the MCP server gives Claude a way to inspect real data when you need to validate a response shape or debug a 401.

## What ships

### API knowledge in `.claude/CLAUDE.md`

Loaded every session. Covers:

- Ticker prefixes across six asset classes (equities, options, crypto, forex, indices, futures)
- SDK method name maps for Python, JavaScript, Go, and Kotlin (same operations, different names in each)
- Pagination behavior: `list_*` auto-paginates, `get_*` returns single objects, `limit` is page size not total results
- Plan tier gates, so Claude doesn't recommend quotes on Basic or Greeks without Options Starter
- Common 401 / 429 / empty-result debugging patterns
- Rate-limit retry helpers, including the non-obvious detail that the Python SDK's `BadResponse` body matches on text (`"maximum requests"`, `"rate limit"`) instead of HTTP status

### Five skills

| Command | What it does |
|---|---|
| `/massive:scaffold my-app rest python` | New project with dependencies, `.env`, and working boilerplate. Python, JS/TS, Go, or Kotlin. Checks plan tier before scaffolding WebSocket or Streamlit projects that need Starter. |
| `/massive:discover "options Greeks for SPY"` | Finds the right endpoint and shows SDK usage in your language. |
| `/massive:debug` | Diagnoses API errors, empty results, and SDK quirks across all four languages. Covers the Python `BadResponse` rate-limit pattern, Go nil-pointer guards, JS object-param shape, Kotlin JitPack deps. |
| `/massive:options "iron condor" SPY python` | Builds a runnable options strategy as a project. Screens the chain, calculates max profit / max loss / breakeven, ranks by risk-reward. Expiration dates are derived from today, not hardcoded. |
| `/massive:dashboard my-dash multi-asset` | Modular Streamlit dashboard with a cached data layer and Plotly charts. Four focus areas: multi-asset, options, crypto, macro. |

### Live API via MCP (optional, installed separately)

The [Massive MCP server](https://github.com/massive-com/mcp_massive) is a separate install (see [Getting started](#2-install-the-massive-mcp-server-optional), steps 2-3). Once registered with `claude mcp add`, Claude gets three tools:

- `search_endpoints(query)`: find endpoints by natural-language description.
- `call_api(endpoint, params, store_as)`: call a REST endpoint and optionally save the response as a DataFrame.
- `query_data(sql)`: run SQL against stored DataFrames, with built-in financial functions (Black-Scholes, Sharpe, returns, SMA, EMA).

Reach for these when you need to see what an endpoint actually returns before writing code against it, or when something in your code isn't returning what you expected. REST endpoints are polled. Real-time streaming lives on the WebSocket feeds, not in these tools.

Skip the MCP install if you only want knowledge + skills. The plugin still works; you just won't get live-data lookups from inside a session.

## Getting started

### 1. Prereqs

- [Claude Code](https://claude.ai/code) CLI. Check with `claude --version`.
- [uv](https://docs.astral.sh/uv/), to install the Massive MCP server (only needed for live-API features). Check with `uv --version`. Install with `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS or Linux) or `pip install uv`.
- A Massive API key from [massive.com/dashboard](https://massive.com/dashboard). The free Basic tier is enough to start (end-of-day data, 5 calls/min).

For scaffolding in languages other than Python, you'll also need Node.js 16+, Go 1.21+, or JDK 21+ with Gradle, depending on the language you pick. The plugin itself doesn't require these; they only matter when `/massive:scaffold` creates a project in that language and you want to run it.

### 2. Install the Massive MCP server (optional)

The [Massive MCP server](https://github.com/massive-com/mcp_massive) lets Claude inspect real API responses, fetch live data for debugging, and explore endpoints before writing code. Install it once as a shared `uv` tool on your `$PATH`:

```bash
uv tool install git+https://github.com/massive-com/mcp_massive
```

`mcp_massive` is now shared across Claude Code and any other MCP-aware tool (Codex, for example). Upgrade later with `uv tool upgrade mcp-massive`. For alternate install paths and advanced options, see the [mcp_massive repo](https://github.com/massive-com/mcp_massive).

Skip if you don't need live-API features. The plugin's knowledge and skills still work without it.

### 3. Register the MCP server with Claude Code (optional)

```bash
claude mcp add massive --scope user \
  --env MASSIVE_API_KEY=your_key -- \
  mcp_massive
```

This writes the server entry into `~/.claude.json` so every Claude Code session uses it. Rotate the key later with `claude mcp remove massive` followed by the same `add` command with the new key. Skip if you skipped step 2.

### 4. Install the plugin

```bash
claude plugin marketplace add massive-com/claude-code-plugin
claude plugin install massive@massive-claude-code-plugin
```

Knowledge loads in every Claude Code session on this machine. No per-project setup, no key prompt (the key lives with the MCP server you set up in step 3, not the plugin).

### 5. Verify it works

Open Claude Code in any directory and check:

1. Run `/reload-plugins`. Expect `1 plugins · 5 skills · 0 errors`.
2. Run `/mcp`. Expect `massive` listed as connected (if you did steps 2-3).
3. Ask: `Call the Massive API for AAPL's last trade.` Should return a live price when the MCP server is registered, or a note that live data isn't available when it isn't.

If anything fails, jump to [Troubleshooting](#troubleshooting).

### 6. Try it out

Point Claude at a directory (new or existing) and scaffold your first project:

```
/massive:scaffold earnings-tracker rest python
```

That creates a working Python project. Then:

```bash
cd earnings-tracker
cp .env.example .env     # add your Massive API key
uv sync
uv run python main.py    # prints real AAPL daily bars
```

From there, ask natural questions and Claude will reach for the right skill or MCP tool as needed:

```
You:    Show me AAPL's last 30 days and calculate the Sharpe ratio.
Claude: [uses call_api via MCP, stores the result, runs sharpe_ratio, prints a number]

You:    Now build the same thing in Node.js.
Claude: /massive:scaffold earnings-tracker-js rest javascript
        [scaffolds a JS project with getStocksAggregates() and the right object-params syntax]
```

Common follow-on moves: `/massive:discover "options Greeks for SPY"` to find an endpoint, `/massive:debug` when something errors, `/massive:options "iron condor" SPY python` or `/massive:dashboard my-dash multi-asset` to scaffold more specialized projects.

## Local development

If you're working on this plugin itself, or want to try it before installing from the marketplace:

```bash
claude --plugin-dir .
```

Run `/reload-plugins` after changes. Expect `1 plugins · 5 skills · 0 errors`.

The plugin no longer bundles an MCP config, so there's nothing tricky here. If you've registered the Massive MCP server at user scope (Getting started steps 2-3), it's available in this local-dev session too. Otherwise, you're running skills + knowledge only.

## Troubleshooting

### MCP server not listed

Run `/mcp` in Claude Code. If `massive` isn't there:

- `mcp_massive` binary missing: run `uv tool install git+https://github.com/massive-com/mcp_massive`. Check with `which mcp_massive`.
- `uv` missing: install it first (`curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`). `mcp_massive` needs Python 3.12+; `uv tool install` fetches it automatically on first use.
- Server not registered: run `claude mcp add massive --scope user --env MASSIVE_API_KEY=your_key -- mcp_massive`. Restart Claude Code.
- Still not visible: run `claude --debug` and look for `mcp_massive` in the log. `claude mcp list` should show `✓ Connected`; if it shows an error, that's your clue.
- Manual smoke test outside Claude Code: running `mcp_massive` in a terminal should start a process that waits for stdin. Ctrl-C to stop.
- Upgrade the server: `uv tool upgrade mcp-massive`.

### Plugin didn't load

- Run `/reload-plugins`; it reports errors inline.
- Confirm `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` are valid JSON.
- For local testing, confirm you're at the repo root when running `claude --plugin-dir .`.

### 401 Unauthorized

The key lives with the MCP server registration, not the plugin. Update it with:

```bash
claude mcp remove massive
claude mcp add massive --scope user --env MASSIVE_API_KEY=new_key -- mcp_massive
```

- **Stale key cached:** restart Claude Code. The MCP subprocess re-reads config at session start.
- **Key rotated or revoked:** regenerate at [massive.com/dashboard](https://massive.com/dashboard) and re-register as above.

### Rate limited (429) on Basic

Basic plan caps at 5 calls per minute. `/massive:debug` has language-specific retry helpers. The Python one is non-obvious: `BadResponse` doesn't preserve the HTTP status code, so you match the body text (`"maximum requests"`, `"rate limit"`) instead. If retries aren't enough, cache reference data for 24 hours, batch via the universal snapshot endpoint instead of per-ticker calls, or move to Starter ($29 to $49/mo).

## Plans

Pricing is per asset class (stocks, options, indices, currencies, futures). Every asset class has a free Basic tier.

| Tier | Price | Data access | Key features |
|---|---|---|---|
| Basic | $0/mo | End-of-day, 2yr history | 5 calls/min, aggregates, reference, technical indicators |
| Starter | $29 to $49/mo | 15-min delayed, 2 to 5yr history | Unlimited calls, WebSockets, flat files, snapshots |
| Developer | $79/mo | 15-min delayed, 4 to 10yr history | Adds trade data |
| Advanced | $99 to $199/mo | Real-time, 5 to 20+yr history | Adds quotes, financials/ratios (stocks) |
| Business | $999 to $2,500/mo | Real-time, full history | Commercial use, no exchange fees, FMV |
| Enterprise | Custom | Everything | SLAs, dedicated support |

Individual tiers are for personal, non-commercial use. Building a product, redistributing data, or embedding this in a SaaS puts you in Business territory.

Add-ons are $99/mo each on individual tiers: Benzinga (news, ratings, earnings), ETF Global (constituents, flows), TMX (corporate events). Annual billing saves 20%. Full breakdown at [massive.com/pricing](https://massive.com/pricing).

## Official SDKs

All skills support Python, JavaScript/TypeScript, Go, and Kotlin.

| Language | Package | Min version | Repo |
|---|---|---|---|
| Python | `massive` on PyPI | 2.5.0 (Python 3.9+) | [massive-com/client-python](https://github.com/massive-com/client-python) |
| JavaScript/TypeScript | `@massive.com/client-js` on npm | 10.6.0 (Node.js 16+) | [massive-com/client-js](https://github.com/massive-com/client-js) |
| Go | `github.com/massive-com/client-go/v3` | 3.2.0 (Go 1.21+) | [massive-com/client-go](https://github.com/massive-com/client-go) |
| Kotlin/JVM | JitPack `com.github.massive-com:client-jvm` | 5.1.2 (JDK 21+, Android SDK 21+) | [massive-com/client-jvm](https://github.com/massive-com/client-jvm) |

## Using a different AI tool?

- [massive-ai-rules](https://github.com/massive-com/massive-ai-rules) has equivalent rule files for Cursor, GitHub Copilot, Windsurf, and Gemini CLI, plus setup guides for Perplexity Spaces and ChatGPT Projects.
- Codex users: [massive-com/codex-plugin](https://github.com/massive-com/codex-plugin).

## Documentation

- [REST API reference](https://massive.com/docs/rest/llms-full.txt): full endpoint catalog, always current
- [Docs index](https://massive.com/docs/llms.txt)
- [Python SDK](https://pypi.org/project/massive/)
- [Community examples and demos](https://github.com/massive-com/community)
- [MCP server source](https://github.com/massive-com/mcp_massive)
- [Claude Code plugins docs](https://docs.anthropic.com/en/docs/claude-code)

## Community

[Facebook](https://www.facebook.com/massivefb) · [X](https://www.x.com/massive_com) · [LinkedIn](https://www.linkedin.com/company/massive-inc) · [YouTube](https://www.youtube.com/@massive_com) · [Reddit](https://www.reddit.com/r/Massive/) · [Instagram](https://www.instagram.com/massive_com)

## License

MIT.

## Disclaimer

Educational material, not investment advice or a recommendation to buy or sell any security. Massive is a market data provider, not a broker-dealer, exchange, or investment adviser. Market data may originate from third-party exchanges and data providers, or may be derived or calculated by Massive; in either case, it is subject to the terms of your Massive subscription. The data and code samples are provided as-is, without warranty of accuracy, completeness, or timeliness. You're responsible for your use of the data and for compliance with all applicable laws and data licensing terms.
