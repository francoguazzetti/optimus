# Sample Queries for Optimus Lite

Ten example prompts that showcase different aspects of the agent's reasoning and tool use.

---

| # | Query | What it demonstrates |
|---|-------|---------------------|
| 1 | **"Which channel had the best CPA last 30 days?"** | `calculate_cpa` tool, ranking logic, single-metric focus |
| 2 | **"Where should I increase budget this week?"** | `get_attribution_insights`, budget recommendation synthesis |
| 3 | **"Compare Paid Search vs Paid Social performance"** | Multi-channel `get_channel_performance`, comparative analysis |
| 4 | **"Give me a full attribution report for the last 90 days"** | `get_attribution_insights` with 90-day window, full report |
| 5 | **"What is the ROAS for Email and Display?"** | `calculate_cpa` filtered by two channels, ROAS focus |
| 6 | **"Which channel drives the most revenue overall?"** | `get_channel_performance` across all channels, revenue ranking |
| 7 | **"Is our Influencer spend worth it?"** | Agent judgment on `calculate_cpa` + `get_attribution_insights` |
| 8 | **"What's the CTR and CVR for Paid Social last 7 days?"** | Short time window, rate-metric focus |
| 9 | **"How many total conversions did we get last 60 days?"** | Aggregated `get_channel_performance`, conversion totals |
| 10 | **"Which channel should I cut budget from and which should I scale?"** | Full attribution + multi-tool reasoning, strategic recommendation |
