"""
LangChain tool: last-click attribution insights and budget recommendations.
"""

import pandas as pd
from langchain_core.tools import tool

from data.mock_data import get_data


@tool
def get_attribution_insights(days: int = 30) -> str:
    """
    Generate a full attribution report using a last-click model.

    Identifies top and worst performers across all channels and provides
    a concrete budget reallocation recommendation.

    Args:
        days: Number of recent days to include (default 30, max 90).

    Returns:
        Attribution report with channel breakdown, key findings, and budget advice.
    """
    df = get_data()
    cutoff = df["date"].max() - pd.Timedelta(days=days - 1)
    df = df[df["date"] >= cutoff]

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
    summary["revenue_pct"] = (summary["revenue"] / summary["revenue"].sum() * 100).round(1)

    paid = summary[summary["spend"] > 0]
    total_spend = paid["spend"].sum()
    total_revenue = summary["revenue"].sum()
    total_conversions = summary["conversions"].sum()
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0

    best = paid.loc[paid["ROAS"].idxmax()]
    worst_cpa = paid.loc[paid["CPA"].idxmax()]

    lines = [
        f"Attribution Report — Last {days} Days (Last-Click Model)\n{'=' * 50}",
        f"\nOverall Summary",
        f"  Total Spend:       ${total_spend:,.0f}",
        f"  Total Revenue:     ${total_revenue:,.0f}",
        f"  Total Conversions: {total_conversions:,.0f}",
        f"  Overall ROAS:      {overall_roas:.2f}x",
        f"\nChannel Attribution Breakdown:",
    ]

    for _, row in summary.sort_values("revenue_pct", ascending=False).iterrows():
        cpa_str = "N/A" if row["spend"] == 0 else f"${row['CPA']:.2f}"
        roas_str = "∞" if row["spend"] == 0 else f"{row['ROAS']:.2f}x"
        lines.append(
            f"  {row['channel']:<18} {row['revenue_pct']:>5.1f}% revenue"
            f"  | CPA: {cpa_str:<10} | ROAS: {roas_str}"
        )

    lines += [
        f"\nKey Findings",
        f"  Best ROAS:   {best['channel']} ({best['ROAS']:.2f}x)",
        f"  Worst CPA:   {worst_cpa['channel']} (${worst_cpa['CPA']:.2f} per conversion)",
        f"\nBudget Recommendation",
        f"  INCREASE → {best['channel']}: highest return at {best['ROAS']:.2f}x ROAS. "
        f"Consider shifting 15–20% of budget from underperformers here.",
        f"  REVIEW   → {worst_cpa['channel']}: CPA of ${worst_cpa['CPA']:.2f} is the "
        f"weakest among paid channels. Audit targeting and creative before next cycle.",
    ]

    return "\n".join(lines)
