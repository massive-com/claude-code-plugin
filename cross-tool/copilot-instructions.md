# Massive API Conventions

You are assisting a developer building with the Massive financial data API. Follow these conventions.

## SDK

The Python SDK is `massive` on PyPI (v2.5.0, requires Python 3.9+). Pin `>=2.4.0` in pyproject.toml. Core imports:

```python
from dotenv import load_dotenv

load_dotenv()  # must come before importing RESTClient

from massive import RESTClient, WebSocketClient
```

Initialize with `RESTClient()` (reads `MASSIVE_API_KEY` from env) or `RESTClient(api_key=key)`.

**Base URL:** `https://api.massive.com`

## Ticker prefixes

- Equities: plain symbols (`AAPL`, `MSFT`)
- Crypto: `X:` prefix (`X:BTCUSD`, `X:ETHUSD`)
- Forex: `C:` prefix (`C:EURUSD`, `C:GBPUSD`)
- Indices: `I:` prefix (`I:SPX`, `I:NDX`, `I:VIX`)
- Options: `O:` prefix with OCC symbology (`O:AAPL250117C00150000`)
- Futures: product codes (`ES`, `NQ`, `CL`, `GC`)

## Key SDK methods

- `list_aggs(ticker, multiplier, timespan, from_, to)` - OHLCV bars
- `list_universal_snapshots(ticker_any_of=[...])` - live snapshot across asset classes
- `list_snapshot_options_chain(underlying_asset, params={})` - options chain with Greeks/IV
- `get_last_trade(ticker)`, `get_last_quote(ticker)` - most recent trade/quote
- `list_trades(ticker)`, `list_quotes(ticker)` - historical trades/quotes
- `get_sma()`, `get_ema()`, `get_rsi()`, `get_macd()` - technical indicators (return `SingleIndicatorResults`; access `.values` for list of data points with `.timestamp` and `.value`)
- `list_stocks_splits(ticker)`, `list_stocks_dividends(ticker)` - corporate actions

Filter operators via `params` dict: `.gt`, `.gte`, `.lt`, `.lte`, `.any_of`.

## Pagination

All `list_` SDK methods return generators that auto-paginate. The `limit` parameter controls page size, not total results. Use `islice()` to cap:

```python
from itertools import islice
bars = list(islice(client.list_aggs("AAPL", 1, "day", "2025-01-01", "2025-06-01"), 200))
```

`get_*` methods (`get_last_trade`, `get_last_quote`, `get_market_status`, `get_sma`, `get_rsi`, etc.) return single result objects, NOT iterators. Do not wrap in `list()` or `islice()`.

## Timestamps

- Aggregates: millisecond epoch in `bar.timestamp`
- Trades: nanosecond epoch in `trade.sip_timestamp`
- Convert: `pd.to_datetime(ts, unit="ms", utc=True)`

## Gotchas

- REST endpoints are polled, not streamed. Only WebSocket provides real-time streaming.
- Futures aggregates use a different endpoint than equity aggregates. The design pattern is consistent, but the endpoints differ.
- Always pass `sort="asc"` to `list_aggs()` for chronological data.
- Options `expiration_date` filtering requires ISO format (`YYYY-MM-DD`).
- Aggregates are split-adjusted by default (`adjusted=True`).
- The SDK `limit` parameter controls page size (max 50,000 for aggregates), not total results. Auto-pagination is on by default.
- Flat files have ~1 day publication delay.
- Free tier (Basic) is limited to 5 calls/min and end-of-day data. WebSockets, flat files, and snapshots require Starter ($29+/mo). Trades require Developer ($79/mo). Quotes, real-time data, and financials require Advanced ($199/mo). Commercial use requires Business plan ($999+/mo). Benzinga, ETF Global, and TMX are separate add-ons ($99/mo per dataset).

## Project structure

Use `uv` for dependency management. Standard layout:
- `main.py` or `streamlit_app.py`
- `pyproject.toml` with `massive>=2.4.0`
- `.env` for `MASSIVE_API_KEY` (gitignored)
- `.env.example` committed with placeholder

## WebSocket

```python
from massive.websocket.models import Market
ws = WebSocketClient(api_key=key, market=Market.Stocks, subscriptions=["T.AAPL"])
ws.run(handle_msg=handler)
```

Subscription prefixes: `T.` trades, `A.` per-minute aggregates, `AS.` per-second aggregates, `Q.` quotes, `FMV.` fair market value.

## Other SDKs

Method names differ across SDKs. Key mappings:

| Python | JS/TS (`@massive.com/client-js`) | Go (`client-go/v3`) | Kotlin (`client-jvm`) |
|---|---|---|---|
| `list_aggs(...)` | `getStocksAggregates({stocksTicker, ...})` | `GetStocksAggregatesWithResponse(...)` | `getAggregatesBlocking(AggregatesParameters(...))` |
| `list_snapshot_options_chain(...)` | `getOptionsChain({underlyingAsset, ...})` | `GetOptionsChainWithResponse(...)` | `getSnapshotOptionsChainBlocking(SnapshotOptionsChainParameters(...))` |
| `get_last_trade(ticker)` | `getLastStocksTrade({stocksTicker})` | `GetLastStocksTradeWithResponse(ctx, ticker)` | `getLastTradeBlockingV2(ticker)` |

JS/TS: ALL methods take a single object parameter with named fields (not positional args). Bar fields are abbreviated (`o`, `h`, `l`, `c`, `v`, `t`). Pagination via `{ pagination: true }` option.

Go: all methods use `WithResponse` suffix. Response data in `resp.JSON200`. Pointer helpers: `rest.Ptr(value)`. Always nil-check before dereferencing.

Kotlin: SDK package is `io.polygon.kotlin.sdk`. Distributed via JitPack (`com.github.massive-com:client-jvm:v5.1.2`). Auth: pass key to `PolygonRestClient(apiKey)` constructor. Methods use `Blocking` suffix: `getAggregatesBlocking(AggregatesParameters(...))`. Bar fields are full names (`open`, `high`, `low`, `close`, `volume`, `timestampMillis`). No auto-pagination.

## Documentation

- Full REST reference: https://massive.com/docs/rest/llms-full.txt
- Python SDK: https://pypi.org/project/massive/
- JS/TS SDK: https://github.com/massive-com/client-js
- Go SDK: https://github.com/massive-com/client-go
- Kotlin SDK: https://github.com/massive-com/client-jvm
- MCP server: https://github.com/massive-com/mcp_massive
