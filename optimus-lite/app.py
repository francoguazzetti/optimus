"""
Streamlit UI for Optimus Lite — Marketing Attribution Agent.

Run with:
    streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage

from agent.graph import run_agent
from data.mock_data import get_data

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Optimus Lite",
    page_icon="📊",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────

df = get_data()

with st.sidebar:
    st.header("📊 Dataset Overview")
    st.metric("Date Range", f"{df['date'].min().strftime('%b %d')} – {df['date'].max().strftime('%b %d, %Y')}")
    st.metric("Channels", int(df["channel"].nunique()))
    st.metric("Total Spend (90d)", f"${df['spend'].sum():,.0f}")
    st.metric("Total Revenue (90d)", f"${df['revenue'].sum():,.0f}")

    st.divider()
    st.subheader("Available Channels")
    for ch in sorted(df["channel"].unique()):
        st.caption(f"• {ch}")

    st.divider()
    st.caption("Optimus Lite · LangGraph + GPT-4o-mini")

# ── Header ────────────────────────────────────────────────────────────────────

st.title("📊 Optimus Lite — Marketing Attribution Agent")
st.caption("Powered by LangGraph + GPT-4o-mini")
st.divider()

# ── Example query buttons ─────────────────────────────────────────────────────

EXAMPLE_QUERIES = [
    "Which channel had the best CPA last 30 days?",
    "Where should I increase budget this week?",
    "Compare Paid Search vs Paid Social performance",
    "Give me a full attribution report for the last 90 days",
]

st.write("**Quick queries — click to run:**")
cols = st.columns(len(EXAMPLE_QUERIES))
for col, query in zip(cols, EXAMPLE_QUERIES):
    if col.button(query, use_container_width=True):
        st.session_state["pending_query"] = query

st.divider()

# ── Chat state ────────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render previous conversation turns
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("reasoning"):
            with st.expander("Agent reasoning"):
                st.code(msg["reasoning"], language="markdown")

# ── Input handling ─────────────────────────────────────────────────────────────

# A button click stores the query in session state; pop it here so it fires once
pending = st.session_state.pop("pending_query", None)
user_input = st.chat_input("Ask about your marketing data...") or pending

if user_input:
    # Show the user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Run the LangGraph agent and display the response
    with st.chat_message("assistant"):
        with st.spinner("Optimus is thinking…"):
            result = run_agent(user_input)

        # Walk through all messages to separate the final answer from tool steps
        final_answer = ""
        reasoning_steps: list[str] = []

        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        reasoning_steps.append(f"→ Calling: {tc['name']}({tc['args']})")
                else:
                    final_answer = msg.content
            elif isinstance(msg, ToolMessage):
                tool_name = getattr(msg, "name", "tool")
                preview = msg.content[:600] + ("…" if len(msg.content) > 600 else "")
                reasoning_steps.append(f"← Result from {tool_name}:\n{preview}")

        st.markdown(final_answer)

        if reasoning_steps:
            with st.expander("Agent reasoning"):
                st.code("\n\n".join(reasoning_steps), language="markdown")

    # Persist to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_answer,
        "reasoning": "\n\n".join(reasoning_steps),
    })
