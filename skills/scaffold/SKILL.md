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

**rest main.py structure:**
1. `from dotenv import load_dotenv` and `load_dotenv()` at top
2. `client = RESTClient()` (reads MASSIVE_API_KEY from env)
3. A sample `list_aggs()` call with `islice()` for pagination
4. Print results in a readable format

**websocket main.py structure:**
1. `from dotenv import load_dotenv` and `load_dotenv()` at top
2. `from massive.websocket.models import Market, Feed`
3. `WebSocketClient(api_key=key, market=Market.Stocks, subscriptions=["T.AAPL"])`
4. A handler function that processes incoming messages
5. `client.run(handle_msg=handler)`

**streamlit streamlit_app.py structure:**
1. `from dotenv import load_dotenv` and `load_dotenv()` at top
2. `@st.cache_resource` for client singleton
3. `@st.cache_data(ttl=30)` for API call wrappers
4. Sidebar for ticker input
5. A price chart using Plotly with `list_aggs()` data
6. Run with `uv run streamlit run streamlit_app.py`

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

**rest structure:**
1. `import 'dotenv/config'`
2. `import { restClient } from '@massive.com/client-js'`
3. `const client = restClient(process.env.MASSIVE_API_KEY)`
4. Sample aggregates call and output

**websocket structure:**
1. `import 'dotenv/config'`
2. `import { websocketClient } from '@massive.com/client-js'`
3. Subscribe to trades, handle messages

### Go

Dependencies: `go.mod`
```
module $0

go 1.18

require github.com/massive-com/client-go/v3 latest
```

Entry point: `main.go`

Run command: `go mod tidy && go run main.go`

.gitignore additions: none needed beyond `.env`

**rest structure:**
1. Read `MASSIVE_API_KEY` from environment (use `os.Getenv` or a `.env` loader like `godotenv`)
2. Create client with `massive.New(massive.WithAPIKey(apiKey))`
3. Sample aggregates call and output

### Kotlin / JVM

Dependencies: `build.gradle.kts`

Entry point: `src/main/kotlin/Main.kt`

Run command: `./gradlew run`

.gitignore additions: `.gradle/`, `build/`

**rest structure:**
1. Read `MASSIVE_API_KEY` from environment
2. Create client
3. Sample aggregates call and output

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
