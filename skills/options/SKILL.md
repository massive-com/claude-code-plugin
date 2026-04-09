---
name: options
description: Build and analyze options strategies using Massive's options data. Supports covered calls, iron condors, spreads, and custom strategies. Use when building options screeners, analyzing Greeks, or constructing multi-leg strategies.
argument-hint: "[strategy] [underlying ticker]"
allowed-tools: mcp__massive__search_endpoints mcp__massive__get_endpoint_docs mcp__massive__call_api mcp__massive__query_data Write Edit Bash Read
---

# Build an options strategy

Strategy: $0
Underlying: $1 (default: SPY if not specified)

## Core SDK pattern for options

```python
from itertools import islice
from massive import RESTClient

client = RESTClient()

# Fetch full options chain with Greeks and IV
chain = list(islice(
    client.list_snapshot_options_chain(
        underlying_asset="AAPL",
        params={
            "expiration_date.gte": "2025-06-01",
            "expiration_date.lte": "2025-06-30",
            "contract_type": "call",  # or "put"
            "limit": 250,
        }
    ),
    1000
))

# Each option has:
for opt in chain:
    strike = opt.details.strike_price
    expiry = opt.details.expiration_date
    contract_type = opt.details.contract_type  # "call" or "put"
    bid = opt.last_quote.bid
    ask = opt.last_quote.ask
    midpoint = opt.last_quote.midpoint
    delta = opt.greeks.delta
    gamma = opt.greeks.gamma
    theta = opt.greeks.theta
    vega = opt.greeks.vega
    iv = opt.implied_volatility
    oi = opt.open_interest
    volume = opt.day.volume
```

## Options ticker format

OCC symbology: `O:AAPL250117C00150000`
- `O:` prefix
- `AAPL` underlying (padded to 6 chars in OCC, but SDK handles this)
- `250117` expiration (YYMMDD)
- `C` or `P` for call/put
- `00150000` strike price * 1000 (8 digits)

## Strategy templates

### Covered call
1. Fetch current stock price via `get_last_trade(underlying)`
2. Fetch call options chain for target expiration
3. Filter: OTM calls (strike > current price), delta between 0.15-0.40
4. Rank by: premium/strike ratio, annualized return, probability OTM

### Iron condor
1. Fetch both call and put chains for target expiration
2. Short call: delta ~0.15-0.20 (OTM)
3. Long call: 1-2 strikes above short call (wing protection)
4. Short put: delta ~(-0.15 to -0.20) (OTM)
5. Long put: 1-2 strikes below short put (wing protection)
6. Calculate: max profit (net credit), max loss (wing width - credit), breakevens

### Vertical spread (bull call / bear put)
1. Fetch chain for target expiration and contract type
2. Buy lower strike, sell higher strike (bull call) or vice versa
3. Calculate: max profit, max loss, breakeven, risk/reward ratio

### Custom screening
1. Fetch full chain
2. Apply user-specified filters (delta range, IV threshold, OI minimum, bid-ask spread)
3. Sort and rank by user criteria
4. Output as formatted table or DataFrame

## MCP server workflow

For interactive analysis, use the MCP tools:

1. `call_api` with `/v3/snapshot/options/{underlying}` and `store_as: "chain"`
2. `query_data` with SQL to filter and rank:
   ```sql
   SELECT * FROM chain
   WHERE greeks_delta BETWEEN 0.15 AND 0.40
   AND implied_volatility > 0.3
   ORDER BY day_volume DESC
   LIMIT 20
   ```

The MCP server has built-in Black-Scholes functions (`bs_price`, `bs_delta`, `bs_gamma`, `bs_theta`, `bs_vega`, `bs_rho`) and return calculations (`simple_return`, `log_return`, `cumulative_return`, `sharpe_ratio`, `sortino_ratio`) available via the `apply` parameter on `call_api`.

## Steps

1. Determine which strategy the user wants from `$0`
2. Get current underlying price
3. Fetch the relevant options chain(s)
4. Apply strategy-specific filtering and ranking
5. Present results with risk/reward metrics
6. Generate reusable Python code the user can run independently
