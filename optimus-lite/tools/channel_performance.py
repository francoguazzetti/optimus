"""
LangChain tool: channel performance summary.
"""

from typing import Optional

import pandas as pd
from langchain_core.tools import tool

from data.mock_data import get_data


@tool
def get_channel_performance(channel: Optional[str] = None, days: int = 30) -> str:
    """
    Retrieve marketing channel performance metrics for the given time window.

    Args:
        channel: Channel name to filter by (optional). One of: Paid Search, Paid Social,
                 Email, Organic, Display, Influencer. Pass None to return all channels.
        days: Number of recent days to include (default 30, max 90).

    Returns:
        Formatted string with spend, impressions, clicks, conversions, revenue, CTR, CVR.
    """
    df = get_data()
    cutoff = df["date"].max() - pd.Timedelta(days=days - 1)
    df = df[df["date"] >= cutoff]

    if channel:
        matched = [c for c in df["channel"].unique() if channel.lower() in c.lower()]
        if not matched:
            available = ", ".join(sorted(df["channel"].unique()))
            return f"Channel '{channel}' not found. Available channels: {available}"
        df = df[df["channel"].isin(matched)]

    summary = (
        df.groupby("channel")
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    summary["CTR"] = (summary["clicks"] / summary["impressions"].replace(0, 1) * 100).round(2)
    summary["CVR"] = (summary["conversions"] / summary["clicks"].replace(0, 1) * 100).round(2)
    summary = summary.sort_values("spend", ascending=False)

    lines = [f"Channel Performance — Last {days} Days\n{'=' * 45}"]
    for _, row in summary.iterrows():
        lines.append(
            f"\n{row['channel']}\n"
            f"  Spend:       ${row['spend']:>10,.0f}\n"
            f"  Impressions: {row['impressions']:>10,.0f}\n"
            f"  Clicks:      {row['clicks']:>10,.0f}\n"
            f"  Conversions: {row['conversions']:>10,.0f}\n"
            f"  Revenue:     ${row['revenue']:>10,.0f}\n"
            f"  CTR:         {row['CTR']:>9.2f}%\n"
            f"  CVR:         {row['CVR']:>9.2f}%"
        )

    return "\n".join(lines)
