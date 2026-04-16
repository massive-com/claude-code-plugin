import os

import streamlit as st
from dotenv import load_dotenv

from terminal.config import DEFAULT_TICKERS
from terminal.data import get_snapshots
from terminal.panels import market_status, price_chart, watchlist

load_dotenv()

st.set_page_config(page_title="Massive Dashboard", layout="wide")

# --- Sidebar ---
st.sidebar.title("Massive Dashboard")

api_key = os.environ.get("MASSIVE_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("API Key", type="password")

if not api_key:
    st.warning("Enter your Massive API key in the sidebar or set MASSIVE_API_KEY in .env.")
    st.stop()

ticker_input = st.sidebar.text_area(
    "Watchlist tickers (one per line)",
    value="\n".join(DEFAULT_TICKERS),
)
tickers = tuple(t.strip() for t in ticker_input.strip().splitlines() if t.strip())

selected_ticker = st.sidebar.selectbox("Chart ticker", tickers, index=0)

st.sidebar.markdown("---")
if st.sidebar.button("Refresh"):
    st.cache_data.clear()
    st.rerun()

# --- Main layout ---
market_status.render(api_key)

st.markdown("---")

snapshots = get_snapshots(api_key, tickers)

col_left, col_right = st.columns([3, 2])

with col_left:
    price_chart.render(api_key, selected_ticker)

with col_right:
    watchlist.render(snapshots)
