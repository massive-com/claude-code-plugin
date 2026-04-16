import streamlit as st

from ..charts import build_candlestick
from ..config import LOOKBACK_DAYS, MULTIPLIER_DEFAULT, TIMESPAN_OPTIONS
from ..data import get_aggs, get_rsi, get_sma


def render(api_key: str, ticker: str):
    st.subheader(f"{ticker} Price Chart")

    col1, col2, col3, col4 = st.columns(4)
    timespan = col1.selectbox("Timespan", TIMESPAN_OPTIONS, index=0, key="chart_timespan")
    multiplier = col2.number_input("Multiplier", min_value=1, max_value=60, value=MULTIPLIER_DEFAULT, key="chart_mult")
    lookback = col3.number_input("Lookback (days)", min_value=7, max_value=365, value=LOOKBACK_DAYS, key="chart_lookback")
    show_indicators = col4.multiselect("Indicators", ["SMA (20)", "RSI (14)"], key="chart_indicators")

    bars = get_aggs(api_key, ticker, multiplier, timespan, lookback)

    if not bars:
        st.warning(f"No aggregate data returned for {ticker}.")
        return

    sma_data = None
    rsi_data = None

    if "SMA (20)" in show_indicators:
        sma_data = get_sma(api_key, ticker, 20, timespan)

    if "RSI (14)" in show_indicators:
        rsi_data = get_rsi(api_key, ticker, 14, timespan)

    fig = build_candlestick(bars, ticker, sma_data=sma_data, rsi_data=rsi_data)
    st.plotly_chart(fig, width="stretch")
