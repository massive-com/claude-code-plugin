# Massive Dashboard

Multi-asset financial dashboard powered by the Massive API. Displays a live watchlist across equities, crypto, forex, and indices alongside interactive candlestick charts with optional SMA and RSI indicators.

## Quickstart

```bash
cp .env.example .env
# Add your Massive API key to .env
uv sync
uv run streamlit run streamlit_app.py
```

## Features

- Multi-asset watchlist with color-coded price changes
- Candlestick chart with configurable timespan, multiplier, and lookback
- Optional SMA (20) and RSI (14) overlays
- Market status indicators (NYSE, NASDAQ, Crypto, Forex)
- TTL-based caching to minimize API calls

## Docs

https://massive.com/docs
