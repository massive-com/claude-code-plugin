---
name: discover
description: Find the right Massive API endpoint for a financial data task. Use when the user needs to find which endpoint returns specific market data, or when exploring what data is available for a given asset class or use case.
argument-hint: "[description of data needed]"
allowed-tools: mcp__massive__search_endpoints mcp__massive__get_endpoint_docs Read
---

# Find the right Massive endpoint

The user needs: $ARGUMENTS

## Process

1. Use `search_endpoints` to find candidate endpoints matching the user's description. Try multiple search terms if the first query returns few results. For example, if "options Greeks" returns little, also try "options chain snapshot."

2. For the top 2-3 matches, use `get_endpoint_docs` to pull full parameter documentation.

3. Present results to the user in this format for each relevant endpoint:

   **Endpoint:** `GET /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}`
   **What it returns:** OHLCV candlestick bars for any supported ticker.
   **Key parameters:** `ticker`, `multiplier`, `timespan` (second/minute/hour/day/week/month/quarter/year), `from`/`to` (YYYY-MM-DD or ms epoch), `adjusted` (default true), `sort` (asc/desc).
   **Plan tier:** Available on all plans.

   **Python SDK:**
   ```python
   from itertools import islice
   from massive import RESTClient

   client = RESTClient()
   bars = list(islice(client.list_aggs("AAPL", 1, "day", "2025-01-01", "2025-06-01"), 200))
   ```

4. If the data need spans multiple endpoints, explain how they fit together. For example: "Use the snapshot for current price, then aggregates for historical chart data."

5. Note plan tier requirements. Key thresholds:
   - Basic (free): end-of-day data, aggs, reference, technicals, corporate actions. 5 calls/min.
   - Starter ($29-49/mo): adds WebSockets, flat files, snapshots, second aggs. Options Starter adds Greeks/IV.
   - Developer ($79/mo): adds trades.
   - Advanced ($99-199/mo): adds quotes, real-time data. Stocks Advanced adds financials/ratios.
   - Business ($999-2,500/mo): commercial use, FMV, no exchange fees.
   - Partner data (Benzinga, ETF Global, TMX): separate add-ons, $99/mo per dataset.

## Ticker prefix reminder

- Equities: plain (`AAPL`)
- Crypto: `X:` prefix (`X:BTCUSD`)
- Forex: `C:` prefix (`C:EURUSD`)
- Indices: `I:` prefix (`I:SPX`)
- Options: `O:` prefix (`O:AAPL250117C00150000`)
- Futures: product codes (`ES`, `NQ`)
