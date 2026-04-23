<img src="images/logo_new.png" alt="Massive" width="100%"/>

# Massive Claude Code Plugin

Build financial applications faster with [Massive](https://massive.com) market data and [Claude Code](https://claude.ai/code). This plugin gives Claude direct knowledge of the Massive API and live access to market data across equities, options, crypto, forex, indices, and futures.

## What this does

When you install this plugin, every Claude Code session automatically gets:

**API knowledge.** Claude knows Massive's ticker formats, SDK patterns, pagination behavior, plan tiers, and common pitfalls. You do not need to explain how the API works.

**Live API access.** The [Massive MCP server](https://github.com/massive-com/mcp_massive) starts automatically. Claude can search 200+ endpoints, read their documentation, call the API with your key, store results as DataFrames, and run SQL against them.

**Interactive skills.** Five slash commands for common workflows:

| Command | What it does |
|---|---|
| `/massive:scaffold my-app rest python` | Create a new project with dependencies, .env, and working boilerplate. Supports Python, JavaScript/TypeScript, Go, and Kotlin. |
| `/massive:discover "options Greeks for SPY"` | Find the right API endpoint and show SDK usage in your language |
| `/massive:debug` | Diagnose API errors, empty results, or SDK issues across all languages |
| `/massive:options "iron condor" SPY python` | Build an options strategy as a runnable project with risk/reward analysis |
| `/massive:dashboard my-dash multi-asset` | Scaffold a Streamlit financial dashboard with modular architecture |

## Example workflow

```
You:    /massive:scaffold earnings-tracker rest python
Claude: [creates project directory with pyproject.toml, .env.example, main.py, README]

You:    Show me AAPL's last 30 days of daily bars and calculate the Sharpe ratio
Claude: [calls the API via MCP, stores results, runs sharpe_ratio calculation, shows output]

You:    Now build the same thing in Node.js
Claude: /massive:scaffold earnings-tracker-js rest javascript
        [creates package.json, index.js with getStocksAggregates({...}), .env.example]
```

## Installation

**1. Get an API key** at [massive.com/dashboard](https://massive.com/dashboard). A free Basic plan works for testing (5 calls/min, end-of-day data, 2yr history).

**2. Install the plugin:**
```bash
claude plugin marketplace add massive-com/claude-code-plugin
claude plugin install massive@massive-com-claude-code-plugin
```

You will be prompted for your API key (stored in your system keychain).

**3. Start building.** Open Claude Code in any directory. The plugin loads automatically.

### Local development

To test the plugin from a local clone of this repo:
```bash
claude --plugin-dir .
```

To reload after changes without restarting, run `/reload-plugins` inside Claude Code.

### Verify your setup

Open Claude Code in any directory, then confirm three things:

1. **Plugin loaded.** Run `/reload-plugins` and check for `1 plugins, 5 skills, 0 errors`.
2. **MCP server running.** Ask: `What MCP tools do you have from Massive?` Claude should list `search_endpoints`, `get_endpoint_docs`, `call_api`, `query_data`.
3. **API key working.** Ask: `Call the Massive API for AAPL's last trade.` You should get a live price back.

If any step fails, see the [Troubleshooting](#troubleshooting) section below.

## Troubleshooting

### MCP server does not start

The Massive MCP server is spawned via [`uvx`](https://docs.astral.sh/uv/guides/tools/) and requires Python 3.12+.

- **`uvx: command not found`** — Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or `pip install uv`.
- **Python too old** — Check with `python3 --version`. uvx will fetch Python 3.12 automatically the first time, but this requires network access. If you are offline, install Python 3.12 manually.
- **No MCP tools available in Claude** — Restart Claude Code. If it persists, run with `claude --debug` and look for `mcp_massive` entries in the logs.
- **First launch is slow** — On the first run, uvx downloads the MCP server package (~5-10 seconds). Subsequent launches are fast.

### Plugin did not load

- Run `/reload-plugins` inside Claude Code; it reports errors inline.
- Confirm `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` exist and parse as valid JSON.
- For local testing, verify you are in the repo root when running `claude --plugin-dir .`.

### API calls return 401 Unauthorized

- **Installed via marketplace:** The API key is stored in your system keychain. Reinstall to re-prompt: `claude plugin uninstall massive@massive-com-claude-code-plugin && claude plugin install massive@massive-com-claude-code-plugin`.
- **Local testing (`--plugin-dir`):** The plugin does not prompt for a key in local mode. Export it before starting Claude Code: `export MASSIVE_API_KEY=your_key` then `claude --plugin-dir .`.
- **Key revoked or rotated:** Get a fresh key at [massive.com/dashboard](https://massive.com/dashboard) and reinstall the plugin.

### Rate-limited (429) on Basic tier

The free Basic plan is capped at 5 calls/min. If you hit 429s, see the retry and caching guidance in `/massive:debug` or upgrade to Starter ($29-49/mo) for unlimited calls.

## Plans and pricing

Plans are per asset class (Stocks, Options, Indices, Currencies, Futures). A free tier is available for every asset class.

| Tier | Price | Data | Key features |
|---|---|---|---|
| Basic | $0/mo | End-of-day, 2yr history | 5 calls/min, aggregates, reference data, technical indicators |
| Starter | $29-49/mo | 15-min delayed, 2-5yr history | Unlimited calls, WebSockets, flat files, snapshots |
| Developer | $79/mo | 15-min delayed, 4-10yr history | Adds trade data |
| Advanced | $99-199/mo | Real-time, 5-20+yr history | Adds quotes, financials/ratios (stocks) |
| Business | $999-2,500/mo | Real-time, full history | Commercial use, no exchange fees, FMV |
| Enterprise | Custom | Everything | SLAs, dedicated support |

**Individual vs Business:** Individual plans are for personal, non-commercial projects. If you are building a product, SaaS, or redistributing data, you need a Business plan.

**Partner data** (Benzinga, ETF Global, TMX) is available as add-ons at $99/mo per dataset. Annual billing saves 20%.

Full pricing details: [massive.com/pricing](https://massive.com/pricing)

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- [uv](https://docs.astral.sh/uv/) (for MCP server installation)
- Python 3.12+ (required by the MCP server; the Python SDK supports 3.9+)
- A Massive API key ([massive.com/dashboard](https://massive.com/dashboard))

For non-Python scaffolding:
- **JavaScript/TypeScript:** Node.js 16+
- **Go:** Go 1.21+
- **Kotlin:** JDK 21+ and Gradle

## Official SDKs

All skills support Python, JavaScript/TypeScript, Go, and Kotlin. Massive provides official client libraries for each:

| Language | Package | Minimum version | Repository |
|---|---|---|---|
| Python | `massive` on PyPI | v2.5.0 (Python 3.9+) | [massive-com/client-python](https://github.com/massive-com/client-python) |
| JavaScript/TypeScript | `@massive.com/client-js` on npm | v10.6.0 (Node.js 16+) | [massive-com/client-js](https://github.com/massive-com/client-js) |
| Go | `github.com/massive-com/client-go/v3` | v3.2.0 (Go 1.21+) | [massive-com/client-go](https://github.com/massive-com/client-go) |
| Kotlin/JVM | JitPack `com.github.massive-com:client-jvm` | v5.1.2 (JDK 21+, Android SDK 21+) | [massive-com/client-jvm](https://github.com/massive-com/client-jvm) |

## Other AI coding assistants

Using a different AI tool? The [**massive-ai-rules**](https://github.com/massive-com/massive-ai-rules) repo has equivalent instruction files for Cursor, GitHub Copilot, Gemini CLI, Windsurf, and more, plus setup guides for Perplexity Spaces and ChatGPT Projects.

For OpenAI Codex users, see the [**Massive Codex plugin**](https://github.com/massive-com/codex-plugin).

## Documentation

- [REST API reference](https://massive.com/docs/rest/llms-full.txt) (full endpoint catalog)
- [Python SDK](https://pypi.org/project/massive/)
- [Community examples and demos](https://github.com/massive-com/community)
- [MCP server](https://github.com/massive-com/mcp_massive)
- [Claude Code plugins](https://docs.anthropic.com/en/docs/claude-code)

## Community

- [Facebook](https://www.facebook.com/massivefb)
- [X (Twitter)](https://www.x.com/massive_com)
- [LinkedIn](https://www.linkedin.com/company/massive-inc)
- [YouTube](https://www.youtube.com/@massive_com)
- [Reddit](https://www.reddit.com/r/Massive/)
- [Instagram](https://www.instagram.com/massive_com)

## License

MIT

## Disclaimer

This content is for educational purposes only. Nothing in this post constitutes investment advice or a recommendation to buy or sell any securities or other financial instruments. Massive is a market data provider, not a broker-dealer, exchange, or investment adviser. Market data accessed through Massive may originate from third-party exchanges and data providers or may be derived or calculated by Massive; in either case, it is subject to the applicable terms of your Massive subscription agreement. The data and code samples provided by Massive are offered on an "as-is" basis without any warranty of accuracy, completeness, or timeliness. You are solely responsible for your use of the data provided by Massive and for compliance with all applicable terms and conditions, laws, and data licensing requirements.
