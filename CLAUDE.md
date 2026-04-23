# Massive Claude Code Plugin

This repo is a standalone Claude Code plugin for Massive, a financial data API platform. Customers install it to get API knowledge, interactive skills, and auto-configured MCP connectivity when building with Massive.

## Repo structure

```
.claude-plugin/
  plugin.json                  - Plugin manifest (name: "massive", v1.0.0)
  marketplace.json             - Single-plugin marketplace for distribution
.claude/
  CLAUDE.md                    - Customer-facing API knowledge (loaded every session)
skills/                        - 5 interactive skills (slash commands)
  scaffold/SKILL.md            - /massive:scaffold - new project boilerplate
  discover/SKILL.md            - /massive:discover - find the right API endpoint
  debug/SKILL.md               - /massive:debug - diagnose API errors
  options/SKILL.md             - /massive:options - build options strategies
  dashboard/SKILL.md           - /massive:dashboard - scaffold Streamlit dashboards
.mcp.json                      - Auto-configures the Massive MCP server (tracks latest upstream via uvx --refresh)
README.md                      - Installation and usage docs
```

## Key dependencies

- MCP server: `massive-com/mcp_massive` (spawned via `uvx --refresh` from git HEAD, requires Python 3.12+)
- Python SDK: `massive` on PyPI (v2.5.0, Python 3.9+)
- Also: JS/TS (`@massive.com/client-js`), Go (`client-go`), Kotlin/JVM (`client-jvm`)
- MCP server indexes endpoints from `massive.com/docs/rest/llms-full.txt`

## Installation (for customers)

```bash
claude plugin marketplace add massive-com/claude-code-plugin
claude plugin install massive@massive-com-claude-code-plugin
```

## Local testing

```bash
claude --plugin-dir .
```

## Brand and terminology

- REST endpoints are "polled," never "streamed" (only WebSocket streams)
- Individual tickers are not "markets." Markets are asset classes (equities, crypto, forex, etc.)
- Futures aggregates use a different endpoint than equity aggregates. Say "one consistent API design pattern," not "one endpoint"
- Never say "stock data app." Use: financial dashboards, quantitative analysis, algorithmic trading, fintech applications
- No emojis in any content
- No em dashes. Use commas, periods, semicolons, or parentheses
