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
| `/massive:scaffold my-app rest` | Create a new project with pyproject.toml, .env, and working boilerplate |
| `/massive:discover "options Greeks for SPY"` | Find the right API endpoint and show SDK usage |
| `/massive:debug` | Diagnose API errors, empty results, or SDK issues |
| `/massive:options "iron condor" SPY` | Build and analyze options strategies with live chain data |
| `/massive:dashboard my-dash multi-asset` | Scaffold a Streamlit financial dashboard |

## Example workflow

```
You:    /massive:scaffold earnings-tracker rest
Claude: [creates project directory with pyproject.toml, .env.example, main.py, README]

You:    Show me AAPL's last 30 days of daily bars and calculate the Sharpe ratio
Claude: [calls the API via MCP, stores results, runs sharpe_ratio calculation, shows output]

You:    Now add a chart of that data using Plotly
Claude: [writes the chart code using the correct SDK patterns and timestamp handling]
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

## Official SDKs

This plugin focuses on Python, but Massive provides official client libraries for multiple languages:

| Language | Package | Repository |
|---|---|---|
| Python | `massive` on PyPI | [massive-com/client-python](https://github.com/massive-com/client-python) |
| JavaScript/TypeScript | `@massive.com/client-js` on npm | [massive-com/client-js](https://github.com/massive-com/client-js) |
| Go | `github.com/massive-com/client-go/v3` | [massive-com/client-go](https://github.com/massive-com/client-go) |
| Kotlin/JVM | Gradle (Android SDK 21+) | [massive-com/client-jvm](https://github.com/massive-com/client-jvm) |

## Cross-tool support

For developers using other AI coding assistants, equivalent API convention files are included:

- **Cursor:** Copy `cross-tool/.cursorrules` to `.cursor/rules/massive.mdc` in your project.
- **GitHub Copilot:** Copy `cross-tool/copilot-instructions.md` to `.github/copilot-instructions.md` in your project.

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
