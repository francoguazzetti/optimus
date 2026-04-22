# Optimus Lite — Marketing Attribution Agent

> A LangGraph-powered AI analyst that answers marketing performance questions using real tool calls, structured data, and opinionated recommendations.

---

## What is this?

Optimus Lite is a **ReAct-style AI agent** built with LangGraph and LangChain that acts as a marketing attribution analyst for a LATAM e-commerce company. You ask questions in plain English — the agent reasons about which tools to call, fetches the data, and returns a concise, data-driven recommendation.

This is a portfolio project demonstrating LangGraph agent architecture applied to real marketing analytics problems.

---

## Architecture

```
User (Streamlit UI)
        │
        ▼
  ┌─────────────┐
  │  app.py     │  Streamlit chat interface
  └──────┬──────┘
         │  user query
         ▼
  ┌─────────────────────────────────────┐
  │         LangGraph Agent             │
  │                                     │
  │  START → call_llm ──┐               │
  │              ▲      │ tool_calls?   │
  │              │      ▼               │
  │         call_tools (ToolNode)       │
  │              │      │               │
  │              └──────┘  no → END     │
  └──────────────────┬──────────────────┘
                     │ tool calls
         ┌───────────┼───────────┐
         ▼           ▼           ▼
  get_channel_  calculate_  get_attribution_
  performance     cpa         insights
         │           │           │
         └───────────┴───────────┘
                     │
                     ▼
              data/mock_data.py
          (90-day LATAM e-commerce dataset)
```

---

## Tech Stack

- **LangGraph** — agent graph, state management, ReAct loop
- **LangChain** — tool decorators, message types, LLM abstraction
- **langchain-openai** — ChatOpenAI (GPT-4o-mini)
- **Streamlit** — chat UI with reasoning expander
- **Pandas + NumPy** — mock dataset generation and aggregation
- **python-dotenv** — environment variable management

---

## Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd optimus-lite

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your OpenAI key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 5. Run the app
streamlit run app.py
```

---

## Example Queries

| Query | Expected output |
|-------|----------------|
| "Which channel had the best CPA last 30 days?" | Ranked CPA table, winner highlighted with recommendation to scale |
| "Where should I increase budget this week?" | Attribution insights + specific channel to shift budget toward |
| "Compare Paid Search vs Paid Social performance" | Side-by-side metrics: spend, CTR, CVR, conversions, revenue |
| "Give me a full attribution report for the last 90 days" | Complete last-click breakdown with revenue %, ROAS, and budget advice |

---

## How It Works (ReAct Loop)

1. **User sends a query** via the Streamlit chat interface.
2. **call_llm node** — GPT-4o-mini receives the system prompt + conversation history and decides which tool(s) to call.
3. **call_tools node** — LangGraph's `ToolNode` executes the tool and appends the result as a `ToolMessage`.
4. **Loop back** — the LLM sees the tool result and either calls another tool or produces a final answer.
5. **END** — the final `AIMessage` (no tool calls) is displayed in the UI. Intermediate steps are shown in the "Agent reasoning" expander.

---

## Project Structure

```
optimus-lite/
├── app.py                    # Streamlit UI
├── requirements.txt
├── .env.example
├── data/
│   └── mock_data.py          # 90-day LATAM e-commerce mock dataset
├── tools/
│   ├── __init__.py
│   ├── channel_performance.py
│   ├── cpa_calculator.py
│   └── attribution.py
├── agent/
│   ├── __init__.py
│   ├── graph.py              # LangGraph ReAct agent
│   └── prompts.py            # System prompt
└── examples/
    └── sample_queries.md     # 10 example queries
```

---

Built as part of a portfolio to demonstrate LangGraph agent architecture applied to real marketing analytics problems.
