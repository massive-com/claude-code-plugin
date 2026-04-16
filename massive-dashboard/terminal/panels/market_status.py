import streamlit as st

from ..config import COLORS
from ..data import get_market_status


def render(api_key: str):
    st.subheader("Market Status")

    status = get_market_status(api_key)

    if not status:
        st.info("Unable to fetch market status.")
        return

    markets = {}
    if hasattr(status, "exchanges"):
        exchanges = status.exchanges
        if hasattr(exchanges, "nyse"):
            markets["NYSE"] = getattr(exchanges, "nyse", "unknown")
        if hasattr(exchanges, "nasdaq"):
            markets["NASDAQ"] = getattr(exchanges, "nasdaq", "unknown")
        if hasattr(exchanges, "otc"):
            markets["OTC"] = getattr(exchanges, "otc", "unknown")
    if hasattr(status, "currencies"):
        currencies = status.currencies
        if hasattr(currencies, "crypto"):
            markets["Crypto"] = getattr(currencies, "crypto", "unknown")
        if hasattr(currencies, "fx"):
            markets["Forex"] = getattr(currencies, "fx", "unknown")

    if not markets:
        st.write("No detailed exchange status available.")
        return

    cols = st.columns(len(markets))
    for i, (name, state) in enumerate(markets.items()):
        state_str = str(state).lower()
        if state_str == "open":
            color = COLORS["green"]
        elif state_str == "closed":
            color = COLORS["red"]
        else:
            color = COLORS["muted"]
        cols[i].markdown(
            f"**{name}**<br><span style='color:{color}'>{state_str.upper()}</span>",
            unsafe_allow_html=True,
        )
