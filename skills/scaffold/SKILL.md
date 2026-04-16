---
name: scaffold
description: Scaffold a new Massive API project with dependency files, .env setup, and boilerplate code. Use when creating a new project, demo, or example that uses Massive's financial data APIs.
argument-hint: "[project-name] [type: rest|websocket|streamlit] [language: python|javascript|typescript|go|kotlin]"
disable-model-invocation: false
allowed-tools: Write Edit Bash
---

# Scaffold a new Massive project

Create a new project called `$0` of type `$1` (default: `rest` if not specified).
Language: `$2` (default: `python` if not specified). Infer from context if the user mentions a language or SDK.

## Project types

**rest** (default): CLI script for data fetching and analysis.
**websocket**: Real-time streaming script with a handler callback.
**streamlit**: Interactive dashboard with Plotly charts and cached API calls (Python only).

## Language-specific setup

### Python

Dependencies: `pyproject.toml`
```toml
[project]
name = "$0"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "massive>=2.4.0",
    "python-dotenv>=1.0.0",
]
```

For **streamlit** type, add:
```toml
    "streamlit>=1.41.0",
    "plotly>=5.24.0",
    "pandas>=2.2.0",
```

Entry point: `main.py` (or `streamlit_app.py` for streamlit type)

Run command: `uv sync && uv run python main.py`

.gitignore additions: `.venv/`, `__pycache__/`, `.uv/`, `uv.lock`

**rest main.py:**
```python
from itertools import islice
from datetime import datetime, timezone
from dotenv import load_dotenv
from massive import RESTClient

load_dotenv()
client = RESTClient()  # reads MASSIVE_API_KEY from .env

bars = list(islice(client.list_aggs("AAPL", 1, "day", "2025-01-01", "2025-06-01", sort="asc"), 30))
for bar in bars:
    dt = datetime.fromtimestamp(bar.timestamp / 1000, tz=timezone.utc)
    print(f"{dt:%Y-%m-%d}  O:{bar.open:.2f}  H:{bar.high:.2f}  L:{bar.low:.2f}  C:{bar.close:.2f}  V:{bar.volume:.0f}")
```
Timestamps are millisecond epoch integers. Convert with `datetime.fromtimestamp(bar.timestamp / 1000)` or `pd.to_datetime(bar.timestamp, unit="ms", utc=True)`. Do NOT use strftime directly on bar.timestamp.

**websocket main.py:**
```python
import os
from dotenv import load_dotenv
from massive import WebSocketClient
from massive.websocket.models import Market, Feed

load_dotenv()

ws = WebSocketClient(
    api_key=os.environ["MASSIVE_API_KEY"],
    market=Market.Stocks,
    feed=Feed.Delayed,  # use Feed.RealTime for Advanced/Business plans
    subscriptions=["T.AAPL"],
)

def handle_msg(msgs):
    for m in msgs:
        print(f"Trade: {m.price} x {m.size}")

ws.run(handle_msg=handle_msg)
```

**streamlit streamlit_app.py structure:**
1. `from dotenv import load_dotenv` and `load_dotenv()` at top
2. `@st.cache_resource` for client singleton
3. `@st.cache_data(ttl=30)` for API call wrappers
4. Sidebar for ticker input
5. A price chart using Plotly with `list_aggs()` data
6. Timestamps: `pd.to_datetime(bar.timestamp, unit="ms", utc=True)`
7. Run with `uv run streamlit run streamlit_app.py`

### JavaScript / TypeScript

Dependencies: `package.json`
```json
{
  "name": "$0",
  "version": "0.1.0",
  "type": "module",
  "dependencies": {
    "@massive.com/client-js": "latest",
    "dotenv": "^16.0.0"
  }
}
```

For TypeScript, add `"devDependencies": { "tsx": "latest", "@types/node": "latest" }` and create a `tsconfig.json`.

Entry point: `index.js` (or `index.ts`)

Run command: `npm install && node index.js` (or `npx tsx index.ts`)

.gitignore additions: `node_modules/`

**rest index.js:**
```javascript
import "dotenv/config";
import { restClient } from "@massive.com/client-js";

const client = restClient(process.env.MASSIVE_API_KEY);

const response = await client.getStocksAggregates("AAPL", 1, "day", "2025-01-01", "2025-06-01", true, "asc", 30);
for (const bar of response.results ?? []) {
  const dt = new Date(bar.t);
  console.log(`${dt.toISOString().slice(0, 10)}  O:${bar.o}  H:${bar.h}  L:${bar.l}  C:${bar.c}  V:${bar.v}`);
}
```
Bar fields are abbreviated: `o` (open), `h` (high), `l` (low), `c` (close), `v` (volume), `t` (Unix ms timestamp). Convert with `new Date(bar.t)`.

Pagination: pass `{ pagination: true }` as third arg to `restClient()` to auto-follow `next_url`. Without it, you get a single page.

**websocket index.js:**
```javascript
import "dotenv/config";
import { websocketClient } from "@massive.com/client-js";

const ws = websocketClient(process.env.MASSIVE_API_KEY, "wss://delayed.massive.com");
const stocksWS = ws.stocks();

stocksWS.onopen = () => {
  stocksWS.send(JSON.stringify({ action: "subscribe", params: "T.AAPL" }));
};

stocksWS.onmessage = ({ data }) => {
  const messages = JSON.parse(data);
  for (const msg of messages) {
    if (msg.ev === "T") {
      console.log(`Trade: ${msg.p} x ${msg.s}`);
    }
  }
};
```
WebSocket message events: `T` (trade), `Q` (quote), `A` (per-second agg), `AM` (per-minute agg). Market connections: `ws.stocks()`, `ws.options()`, `ws.crypto()`, `ws.forex()`, `ws.indices()`, `ws.futures()`.

### Go

Dependencies: `go.mod`
```
module $0

go 1.21

require github.com/massive-com/client-go/v3 latest
```
Also add `github.com/joho/godotenv` for .env loading.

Entry point: `main.go`

Run command: `go mod tidy && go run main.go`

.gitignore additions: none needed beyond `.env`

**rest main.go:**
```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "github.com/joho/godotenv"
    "github.com/massive-com/client-go/v3/rest"
    "github.com/massive-com/client-go/v3/rest/gen"
)

func main() {
    godotenv.Load() // loads .env file
    c := rest.New("") // reads MASSIVE_API_KEY from env

    params := &gen.GetStocksAggregatesParams{
        Adjusted: rest.Ptr(true),
        Sort:     "asc",
        Limit:    rest.Ptr(30),
    }

    resp, err := c.GetStocksAggregatesWithResponse(
        context.Background(), "AAPL", 1, gen.Day, "2025-01-01", "2025-06-01", params,
    )
    if err != nil {
        log.Fatal(err)
    }

    if resp.JSON200 != nil && resp.JSON200.Results != nil {
        for _, bar := range *resp.JSON200.Results {
            dt := time.UnixMilli(int64(bar.Timestamp))
            fmt.Printf("%s  O:%.2f  H:%.2f  L:%.2f  C:%.2f  V:%.0f\n",
                dt.UTC().Format("2006-01-02"), bar.O, bar.H, bar.L, bar.C, bar.V)
        }
    }
}
```
Bar fields: `O`, `H`, `L`, `C`, `V`, `Timestamp` (Unix ms). Pointer helpers: `rest.Ptr(value)` for optional params.

All generated methods follow the pattern `{OperationName}WithResponse`. Response data is in `resp.JSON200`. Results are a pointer to a slice (`*[]T`).

Pagination: auto-pagination is on by default. Disable with `rest.NewWithOptions("", rest.WithPagination(false))`.

**websocket main.go:**
```go
package main

import (
    "fmt"
    "os"
    "os/signal"

    "github.com/joho/godotenv"
    massivews "github.com/massive-com/client-go/v3/websocket"
    "github.com/massive-com/client-go/v3/websocket/models"
)

func main() {
    godotenv.Load()

    c, err := massivews.New(massivews.Config{
        APIKey: os.Getenv("MASSIVE_API_KEY"),
        Feed:   massivews.Delayed,
        Market: massivews.Stocks,
    })
    if err != nil {
        panic(err)
    }
    defer c.Close()

    c.Subscribe(massivews.StocksTrades, "AAPL")
    if err := c.Connect(); err != nil {
        panic(err)
    }

    sigint := make(chan os.Signal, 1)
    signal.Notify(sigint, os.Interrupt)

    for {
        select {
        case <-sigint:
            return
        case <-c.Error():
            return
        case out, more := <-c.Output():
            if !more {
                return
            }
            switch t := out.(type) {
            case models.EquityTrade:
                fmt.Printf("Trade: %.2f x %d\n", t.Price, t.Size)
            }
        }
    }
}
```
WebSocket uses channels: `c.Output()` for messages, `c.Error()` for fatal errors. Topics: `massivews.StocksTrades`, `massivews.StocksQuotes`, `massivews.StocksMinAggs`, etc.

### Kotlin / JVM

Dependencies: `build.gradle.kts`
```kotlin
plugins {
    kotlin("jvm") version "1.9.23"
    application
}

application {
    mainClass.set("MainKt")
}

repositories {
    maven("https://jitpack.io")
    mavenCentral()
}

dependencies {
    implementation("com.github.massive-com:client-jvm:v5.1.2")
    implementation("io.github.cdimascio:dotenv-kotlin:6.4.1")
}
```

Also create `settings.gradle.kts`:
```kotlin
rootProject.name = "$0"
```

Entry point: `src/main/kotlin/Main.kt`

Run command: `./gradlew run`

.gitignore additions: `.gradle/`, `build/`

**rest Main.kt:**
```kotlin
import io.github.cdimascio.dotenv.dotenv
import org.openapitools.client.apis.DefaultApi
import org.openapitools.client.apis.DefaultApi.TimespanGetStocksAggregates
import org.openapitools.client.apis.DefaultApi.SortGetStocksAggregates
import org.openapitools.client.infrastructure.ApiClient
import java.time.Instant
import java.time.ZoneOffset

fun main() {
    val env = dotenv()
    ApiClient.apiKey["apiKey"] = env["MASSIVE_API_KEY"]

    val api = DefaultApi()

    val result = api.getStocksAggregates(
        stocksTicker = "AAPL",
        multiplier = 1,
        timespan = TimespanGetStocksAggregates.day,
        from = "2025-01-01",
        to = "2025-06-01",
        adjusted = true,
        sort = SortGetStocksAggregates.asc,
        limit = 30
    )

    result.results?.forEach { bar ->
        val dt = Instant.ofEpochMilli(bar.t.toLong()).atZone(ZoneOffset.UTC)
        println("${dt.toLocalDate()}  O:${bar.o}  H:${bar.h}  L:${bar.l}  C:${bar.c}  V:${bar.v}")
    }
}
```
Bar fields are abbreviated: `o`, `h`, `l`, `c`, `v`, `t` (Unix ms). Results are nullable (`results?`).

Auth: set `ApiClient.apiKey["apiKey"]` before creating `DefaultApi()`. Use `dotenv-kotlin` for .env loading.

Pagination: manual cursor-based via `nextUrl` on the response. No auto-pagination.

**websocket Main.kt:**
```kotlin
import io.github.cdimascio.dotenv.dotenv
import io.massive.kotlin.sdk.websocket.*

fun main() {
    val env = dotenv()

    val client = MassiveWebSocketClient(
        apiKey = env["MASSIVE_API_KEY"],
        feed = Feed.Delayed,
        market = Market.Stocks,
        listener = object : DefaultMassiveWebSocketListener() {
            override fun onAuthenticated(client: MassiveWebSocketClient) {
                client.subscribeBlocking(listOf(
                    MassiveWebSocketSubscription(MassiveWebSocketChannel.Stocks.Trades, "AAPL")
                ))
            }

            override fun onReceive(client: MassiveWebSocketClient, message: MassiveWebSocketMessage) {
                when (message) {
                    is MassiveWebSocketMessage.StocksMessage.Trade ->
                        println("Trade: ${message.ticker} @ ${message.price}")
                    else -> {}
                }
            }
        }
    )
    client.connectBlocking()
}
```
WebSocket package: `io.massive.kotlin.sdk.websocket`. Client uses listener pattern with `onAuthenticated`, `onReceive`, `onDisconnect`, `onError` callbacks. Subscribe after authentication.

For **websocket type** in Kotlin, add to `build.gradle.kts`:
```kotlin
implementation("com.github.massive-com:client-jvm:v5.1.2")
```
The WebSocket client is included in the same artifact.

## Required files (all languages)

### .env.example
```
MASSIVE_API_KEY=your_api_key_here
```

### .gitignore
Always include:
```
.env
data/
```
Plus language-specific entries listed above.

### README.md
Include:
1. One-line description of what the project does
2. Quickstart: `cp .env.example .env`, add your key, install deps, run
3. Link to Massive docs: https://massive.com/docs

## Plan guidance

After scaffolding, remind the user which plan tier they will need:
- **Basic (free):** Enough for testing with end-of-day aggregates, reference data, technical indicators. Limited to 5 calls/min.
- **Starter ($29-49/mo):** Required for WebSocket streaming, snapshots, flat files, and second aggregates. Options Starter adds Greeks/IV.
- **Developer ($79/mo):** Required for trade data access.
- **Advanced ($99-199/mo):** Required for real-time data, quotes, and financials/ratios (Stocks Advanced).
- **Business ($999+/mo):** Required for commercial use, building products, or redistributing data.

For WebSocket and Streamlit project types, the user will need at least a Starter plan.

## Steps

1. Create the project directory: `$0/`
2. Write all files listed above for the chosen language
3. Confirm the structure and provide the quickstart:
   ```
   cd $0
   cp .env.example .env
   # Add your Massive API key to .env
   ```
   Then the language-specific install and run commands.
4. Note the minimum plan tier needed for the project type
