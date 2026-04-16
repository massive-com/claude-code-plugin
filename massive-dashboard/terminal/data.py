from datetime import datetime, timedelta
from itertools import islice

import streamlit as st
from massive import RESTClient

from .config import TTL_CHART, TTL_INDICATORS, TTL_SNAPSHOT, TTL_MARKET_STATUS


@st.cache_resource
def _get_client(api_key: str) -> RESTClient:
    return RESTClient(api_key=api_key)


@st.cache_data(ttl=TTL_SNAPSHOT, show_spinner=False)
def get_snapshots(api_key: str, tickers: tuple[str, ...]) -> dict:
    client = _get_client(api_key)
    results = {}
    for s in client.list_universal_snapshots(ticker_any_of=list(tickers)):
        results[s.ticker] = s
    return results


@st.cache_data(ttl=TTL_CHART, show_spinner=False)
def get_aggs(api_key: str, ticker: str, multiplier: int, timespan: str, lookback_days: int) -> list:
    client = _get_client(api_key)
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    return list(islice(
        client.list_aggs(ticker, multiplier, timespan, from_date, to_date, sort="asc"),
        5000,
    ))


@st.cache_data(ttl=TTL_INDICATORS, show_spinner=False)
def get_sma(api_key: str, ticker: str, window: int, timespan: str) -> list:
    client = _get_client(api_key)
    result = client.get_sma(ticker, params={"window": window, "timespan": timespan, "sort": "asc"})
    return result.values if result.values else []


@st.cache_data(ttl=TTL_INDICATORS, show_spinner=False)
def get_rsi(api_key: str, ticker: str, window: int, timespan: str) -> list:
    client = _get_client(api_key)
    result = client.get_rsi(ticker, params={"window": window, "timespan": timespan, "sort": "asc"})
    return result.values if result.values else []


@st.cache_data(ttl=TTL_MARKET_STATUS, show_spinner=False)
def get_market_status(api_key: str) -> dict:
    client = _get_client(api_key)
    return client.get_market_status()
