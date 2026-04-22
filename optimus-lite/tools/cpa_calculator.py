"""
LangChain tool: CPA and ROAS calculator.
"""

from typing import Optional

import pandas as pd
from langchain_core.tools import tool

from data.mock_data import get_data


@tool
def calculate_cpa(channel: Optional[str] = None, days: int = 30) -> str:
    """
    Calculate Cost Per Acquisition (CPA) and Return on Ad Spend (ROAS) for channels,
    ranked from best (lowest CPA) to worst.

    Args:
        channel: Channel name to filter by (optional). Pass None to rank all channels.
        days: Number of recent days to include (default 30, max 90).

    Returns:
        Ranked table of channels by CPA with ROAS, spend, and conversion counts.
    """
    df = get_data()
    cutoff = df["date"].max() - pd.Timedelta(days=days - 1)
    df = df[df["date"] >= cutoff]

    if channel:
        matched = [c for c in df["channel"].unique() if channel.lower() in c.lower()]
        if not matched:
            return f"Channel '{channel}' not found."
        df = df[df["channel"].isin(matched)]

    summary = (
        df.groupby("channel")
        .agg(
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    summary["CPA"] = (summary["spend"] / summary["conversions"].replace(0, 1)).round(2)
    summary["ROAS"] = (summary["revenue"] / summary["spend"].replace(0, 0.01)).round(2)

    paid = summary[summary["spend"] > 0].sort_values("CPA").reset_index(drop=True)
    organic = summary[summary["spend"] == 0]

    lines = [f"CPA & ROAS Ranking — Last {days} Days\n{'=' * 45}"]
    lines.append("\nPaid Channels (ranked best → worst CPA):")
    for rank, (_, row) in enumerate(paid.iterrows(), 1):
        lines.append(
            f"\n  #{rank}  {row['channel']}\n"
            f"       CPA:         ${row['CPA']:.2f}\n"
            f"       ROAS:        {row['ROAS']:.2f}x\n"
            f"       Spend:       ${row['spend']:,.0f}\n"
            f"       Conversions: {row['conversions']:,.0f}"
        )

    if not organic.empty:
        lines.append("\nOrganic / Zero-spend Channels:")
        for _, row in organic.iterrows():
            lines.append(
                f"\n  {row['channel']}\n"
                f"       CPA:         N/A (no paid spend)\n"
                f"       Conversions: {row['conversions']:,.0f}\n"
                f"       Revenue:     ${row['revenue']:,.0f}"
            )

    return "\n".join(lines)
