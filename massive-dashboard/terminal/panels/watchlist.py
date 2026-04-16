import streamlit as st

from ..config import COLORS


def render(snapshots: dict):
    st.subheader("Watchlist")

    if not snapshots:
        st.info("No snapshot data available.")
        return

    rows = []
    for ticker, snap in snapshots.items():
        session = getattr(snap, "session", None)
        if session is None:
            rows.append({"Ticker": ticker, "Price": "--", "Change": "--", "Change %": "--"})
            continue

        price = getattr(session, "close", None) or getattr(session, "price", None)
        change = getattr(session, "change", None)
        change_pct = getattr(session, "change_percent", None)

        rows.append({
            "Ticker": ticker,
            "Price": f"{price:.2f}" if price else "--",
            "Change": f"{change:+.2f}" if change is not None else "--",
            "Change %": f"{change_pct:+.2f}%" if change_pct is not None else "--",
        })

    header_cols = st.columns([2, 2, 2, 2])
    header_cols[0].markdown("**Ticker**")
    header_cols[1].markdown("**Price**")
    header_cols[2].markdown("**Change**")
    header_cols[3].markdown("**Change %**")

    for row in rows:
        cols = st.columns([2, 2, 2, 2])
        cols[0].write(row["Ticker"])
        cols[1].write(row["Price"])

        change_str = row["Change"]
        pct_str = row["Change %"]

        if change_str != "--" and change_str.startswith("+"):
            cols[2].markdown(f"<span style='color:{COLORS['green']}'>{change_str}</span>", unsafe_allow_html=True)
        elif change_str != "--" and change_str.startswith("-"):
            cols[2].markdown(f"<span style='color:{COLORS['red']}'>{change_str}</span>", unsafe_allow_html=True)
        else:
            cols[2].write(change_str)

        if pct_str != "--" and pct_str.startswith("+"):
            cols[3].markdown(f"<span style='color:{COLORS['green']}'>{pct_str}</span>", unsafe_allow_html=True)
        elif pct_str != "--" and pct_str.startswith("-"):
            cols[3].markdown(f"<span style='color:{COLORS['red']}'>{pct_str}</span>", unsafe_allow_html=True)
        else:
            cols[3].write(pct_str)
