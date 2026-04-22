"""
Mock marketing dataset simulating a mid-size LATAM e-commerce platform.

Scale is inspired by platforms like MercadoLibre subsidiaries or regional players
operating in Brazil, Mexico, and Argentina — roughly $100K/month in paid media,
tens of thousands of daily sessions, and AOVs between $60-$100 USD.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

CHANNELS = ["Paid Search", "Paid Social", "Email", "Organic", "Display", "Influencer"]

# Per-channel config: (daily_mean, daily_std) for spend, impressions; plus rate means/stds
CHANNEL_CONFIG = {
    "Paid Search": dict(
        spend=(900, 150), impressions=(40_000, 5_000),
        ctr=(0.045, 0.005), cvr=(0.038, 0.005), aov=(85, 15),
    ),
    "Paid Social": dict(
        spend=(650, 120), impressions=(80_000, 10_000),
        ctr=(0.018, 0.003), cvr=(0.022, 0.004), aov=(72, 12),
    ),
    "Email": dict(
        spend=(160, 30), impressions=(25_000, 4_000),
        ctr=(0.062, 0.008), cvr=(0.055, 0.007), aov=(90, 18),
    ),
    "Organic": dict(
        spend=(0, 0), impressions=(30_000, 6_000),
        ctr=(0.038, 0.005), cvr=(0.032, 0.004), aov=(78, 14),
    ),
    "Display": dict(
        spend=(320, 60), impressions=(150_000, 20_000),
        ctr=(0.0008, 0.0002), cvr=(0.008, 0.002), aov=(65, 10),
    ),
    "Influencer": dict(
        spend=(480, 100), impressions=(55_000, 12_000),
        ctr=(0.025, 0.004), cvr=(0.018, 0.003), aov=(95, 20),
    ),
}


def generate_mock_data() -> pd.DataFrame:
    """Generate 90 days of marketing performance data for all channels."""
    np.random.seed(42)
    end_date = date.today()
    start_date = end_date - timedelta(days=89)
    dates = [start_date + timedelta(days=i) for i in range(90)]

    rows = []
    for d in dates:
        # Paid channels see ~25% lower volume on weekends; organic/email stay flat
        is_weekend = d.weekday() >= 5
        paid_factor = 0.75 if is_weekend else 1.0

        for channel, cfg in CHANNEL_CONFIG.items():
            factor = paid_factor if channel not in ("Organic", "Email") else 1.0

            spend = max(0.0, np.random.normal(cfg["spend"][0] * factor, cfg["spend"][1]))
            impressions = max(0, int(np.random.normal(cfg["impressions"][0] * factor, cfg["impressions"][1])))
            ctr = max(0.0, np.random.normal(cfg["ctr"][0], cfg["ctr"][1]))
            clicks = int(impressions * ctr)
            cvr = max(0.0, np.random.normal(cfg["cvr"][0], cfg["cvr"][1]))
            conversions = int(clicks * cvr)
            aov = max(10.0, np.random.normal(cfg["aov"][0], cfg["aov"][1]))
            revenue = round(conversions * aov, 2)

            rows.append({
                "date": d,
                "channel": channel,
                "impressions": impressions,
                "clicks": clicks,
                "spend": round(spend, 2),
                "conversions": conversions,
                "revenue": revenue,
            })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


# Module-level singleton — generated once, shared across all tool calls
_DATA: pd.DataFrame | None = None


def get_data() -> pd.DataFrame:
    """Return the cached mock dataset, generating it on first call."""
    global _DATA
    if _DATA is None:
        _DATA = generate_mock_data()
    return _DATA
