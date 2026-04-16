import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import CHART_HEIGHT, COLORS


def build_candlestick(bars: list, ticker: str, sma_data: list | None = None, rsi_data: list | None = None) -> go.Figure:
    dates = [pd.to_datetime(b.timestamp, unit="ms", utc=True) for b in bars]
    opens = [b.open for b in bars]
    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    closes = [b.close for b in bars]
    volumes = [b.volume for b in bars]

    row_heights = [0.7, 0.15, 0.15] if rsi_data else [0.8, 0.2]
    rows = 3 if rsi_data else 2

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    fig.add_trace(
        go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes, name=ticker),
        row=1, col=1,
    )

    if sma_data:
        sma_dates = [pd.to_datetime(s.timestamp, unit="ms", utc=True) for s in sma_data]
        sma_values = [s.value for s in sma_data]
        fig.add_trace(
            go.Scatter(x=sma_dates, y=sma_values, name="SMA", line=dict(color=COLORS["accent"], width=1.5)),
            row=1, col=1,
        )

    fig.add_trace(
        go.Bar(x=dates, y=volumes, name="Volume", marker_color=COLORS["muted"], opacity=0.5),
        row=2, col=1,
    )

    if rsi_data:
        rsi_dates = [pd.to_datetime(r.timestamp, unit="ms", utc=True) for r in rsi_data]
        rsi_values = [r.value for r in rsi_data]
        fig.add_trace(
            go.Scatter(x=rsi_dates, y=rsi_values, name="RSI", line=dict(color=COLORS["accent"], width=1.5)),
            row=3, col=1,
        )
        fig.add_hline(y=70, line_dash="dash", line_color=COLORS["red"], opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color=COLORS["green"], opacity=0.5, row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["panel_bg"],
        height=CHART_HEIGHT,
        margin=dict(l=50, r=20, t=40, b=20),
        title=dict(text=ticker, font=dict(size=16)),
        xaxis_rangeslider_visible=False,
        showlegend=False,
    )

    fig.update_xaxes(gridcolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"])

    return fig
