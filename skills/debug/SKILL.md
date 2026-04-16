---
name: debug
description: Debug Massive API errors, unexpected responses, or SDK issues. Use when API calls return errors, data looks wrong, pagination isn't working, or the SDK behaves unexpectedly.
disable-model-invocation: false
allowed-tools: Read Grep mcp__massive__search_endpoints mcp__massive__get_endpoint_docs Bash
---

# Debug Massive API issue

Read the user's code and error output, then diagnose the issue.

## Common error patterns

### HTTP 401 Unauthorized
- API key not set or invalid.
- Check: Is `MASSIVE_API_KEY` in `.env`? Is `load_dotenv()` called before `RESTClient()`?
- Check: Is the key correct? Test with `curl -H "Authorization: Bearer YOUR_KEY" "https://api.massive.com/v3/snapshot?ticker.any_of=AAPL"`

### HTTP 403 Forbidden
- Endpoint requires a higher plan tier or add-on.
- Data access unlocks by tier: Basic (end-of-day, aggs, reference) < Starter (+ WebSockets, flat files, snapshots, second aggs) < Developer (+ trades) < Advanced (+ quotes, real-time data, financials/ratios for stocks).
- Partner data (Benzinga, ETF Global, TMX) requires separate add-on subscriptions ($99/mo per dataset for individual).
- Business use (commercial products, redistribution) requires Business plan ($999-2,500/mo per asset class).
- Fair Market Value (FMV) is Business plan only.
- Fix: Check plan at massive.com/dashboard. Suggest which plan tier is needed based on the feature they are trying to access.

### HTTP 404 Not Found
- Wrong ticker format. Check prefix conventions:
  - Crypto needs `X:` prefix (`X:BTCUSD`, not `BTCUSD`)
  - Forex needs `C:` prefix (`C:EURUSD`, not `EURUSD`)
  - Indices need `I:` prefix (`I:SPX`, not `SPX`)
- Wrong endpoint URL or method name in SDK.
- Use `search_endpoints` to find the correct endpoint.

### Empty results (no error)
- Date range falls on a weekend or market holiday. Try a known trading day.
- Ticker is delisted or invalid.
- For flat files: files have a ~1 day publication delay. Data for yesterday may not exist yet.
- For options: check that `expiration_date` is in ISO format (`YYYY-MM-DD`).
- For aggregates: check `from`/`to` date ordering and that `sort="asc"` is set.

### Pagination issues
- SDK `list_` methods return **generators**, not lists. You must iterate or wrap with `list()`.
- The `limit` parameter controls **page size**, not total results. The SDK auto-paginates by default, fetching all pages. To cap total results: `list(islice(client.list_aggs(...), 1000))`.
- To disable auto-pagination: `RESTClient(api_key=key, pagination=False)`.
- Do not call `len()` on a generator. Convert to list first.

### `get_*` method misuse
- `get_*` methods (`get_last_trade`, `get_last_quote`, `get_market_status`, `get_sma`, `get_rsi`, `get_ema`, `get_macd`, etc.) return **single result objects**, not iterators.
- Do NOT wrap them in `list()` or `islice()`. This causes `TypeError: ... object is not iterable`.
- Technical indicators (`get_sma`, `get_rsi`, `get_ema`, `get_macd`) return a `SingleIndicatorResults` object. Access the data via `result.values` (list of objects with `.timestamp` and `.value`).

### Timestamp confusion
- Aggregates: millisecond epoch in `bar.timestamp`.
- Trades: nanosecond epoch in `trade.sip_timestamp`.
- Convert with `pd.to_datetime(ts, unit="ms", utc=True)` or `unit="ns"` for trades.

### WebSocket connection drops
- Check that `market` parameter matches the data type: `Market.Stocks` for equities, `Market.Options` for options, `Market.Crypto` for crypto.
- Subscription format: `T.AAPL` for trades, `A.AAPL` for aggregates, `Q.AAPL` for quotes.
- WebSocket `client.run()` blocks. Run in a daemon thread if combining with other logic.

### SDK version issues
- Ensure `massive>=2.4.0` in `pyproject.toml`. Older versions may be missing methods or endpoints.
- Check installed version: `pip show massive` or `uv pip show massive`.

## Diagnostic steps

1. Read the user's code and identify the failing call.
2. Match the error to a pattern above.
3. If the error doesn't match a known pattern, use `search_endpoints` and `get_endpoint_docs` to verify the endpoint exists and check required parameters.
4. Suggest a specific fix with corrected code.
