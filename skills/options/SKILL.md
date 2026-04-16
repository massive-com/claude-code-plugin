---
name: options
description: Build and analyze options strategies using Massive's options data. Supports covered calls, iron condors, spreads, and custom strategies. Use when building options screeners, analyzing Greeks, or constructing multi-leg strategies.
argument-hint: "[strategy] [underlying ticker] [language: python|javascript|typescript|go]"
allowed-tools: mcp__massive__search_endpoints mcp__massive__get_endpoint_docs mcp__massive__call_api mcp__massive__query_data Write Edit Bash Read
---

# Build an options strategy

Strategy: $0
Underlying: $1 (default: SPY if not specified)
Language: infer from context, default to Python if not specified.

## Output: a runnable project

Create a project directory with the strategy name (e.g., `spy-bull-call-spread/`). The project must include:

1. **Dependency file** (`pyproject.toml`, `package.json`, `go.mod`, etc.)
2. **`.env.example`** with `MASSIVE_API_KEY=your_api_key_here`
3. **`.gitignore`** with `.env` and language-specific entries
4. **Entry point** (`main.py`, `index.js`, `main.go`, etc.) that implements the strategy
5. **README.md** with quickstart instructions

End with:
```
cd <project-name>
cp .env.example .env
# Add your Massive API key to .env
```
Then the language-specific install and run commands.

## Python SDK pattern for options

```python
from itertools import islice
from dotenv import load_dotenv
from massive import RESTClient

load_dotenv()
client = RESTClient()  # reads MASSIVE_API_KEY from .env

# Get current price
last_trade = client.get_last_trade("SPY")  # returns single object, NOT an iterator
spot = last_trade.price

# Fetch options chain (list_ method, returns paginated iterator)
chain = list(islice(
    client.list_snapshot_options_chain(
        underlying_asset="SPY",
        params={
            "expiration_date.gte": "2025-06-01",
            "expiration_date.lte": "2025-06-30",
            "contract_type": "call",
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

## JavaScript/TypeScript SDK pattern

```javascript
import 'dotenv/config';
import { restClient } from '@massive.com/client-js';

const client = restClient(process.env.MASSIVE_API_KEY);

const lastTrade = await client.lastTrade('SPY');
const spot = lastTrade.results.price;

const chain = await client.snapshotOptionChain('SPY', {
  'expiration_date.gte': '2025-06-01',
  'expiration_date.lte': '2025-06-30',
  'contract_type': 'call',
});
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

## MCP server tools

For exploring data before writing code, the MCP tools can help:

1. `call_api` with `/v3/snapshot/options/{underlying}` and `store_as: "chain"`
2. `query_data` with SQL to filter and rank:
   ```sql
   SELECT * FROM chain
   WHERE greeks_delta BETWEEN 0.15 AND 0.40
   AND implied_volatility > 0.3
   ORDER BY day_volume DESC
   LIMIT 20
   ```

Built-in financial functions available via `apply` parameter: Black-Scholes (`bs_price`, `bs_delta`, `bs_gamma`, `bs_theta`, `bs_vega`, `bs_rho`), returns (`simple_return`, `log_return`, `cumulative_return`, `sharpe_ratio`, `sortino_ratio`).

## Steps

1. Determine which strategy the user wants from `$0`
2. Create the project directory
3. Write dependency file, `.env.example`, `.gitignore`
4. Write the entry point script that:
   a. Loads the API key from `.env`
   b. Gets current underlying price
   c. Fetches the relevant options chain(s)
   d. Applies strategy-specific filtering and ranking
   e. Prints results with risk/reward metrics
5. Write README.md
6. Provide quickstart: `cd <project>`, `cp .env.example .env`, install, run
7. Note the minimum plan tier (Options Starter or above for Greeks/IV)
