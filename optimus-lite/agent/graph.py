"""
LangGraph ReAct agent for Optimus Lite.

Graph topology:

    START
      │
      ▼
  call_llm ──(has tool_calls?)──► call_tools
      ▲                                │
      └────────────────────────────────┘
      │
      ▼ (no tool_calls)
     END

The conditional edge after call_llm uses langgraph.prebuilt.tools_condition,
which returns "tools" when the last AIMessage contains tool_calls, else END.
We map "tools" → our "call_tools" node name via the routing dict.
"""

from typing import Annotated

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from agent.prompts import SYSTEM_PROMPT
from tools import ALL_TOOLS


# ── State ─────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """
    Conversation state passed between graph nodes.
    `add_messages` is a reducer that appends new messages rather than replacing the list,
    so every node just returns the new messages it wants to add.
    """
    messages: Annotated[list, add_messages]


# ── LLM node ──────────────────────────────────────────────────────────────────

def call_llm(state: AgentState) -> dict:
    """
    Invoke GPT-4o-mini with the full message history.

    The system prompt is prepended on every call so the model always has the
    analyst persona, regardless of how many tool loops have occurred.
    The LLM decides: call a tool (returns AIMessage with tool_calls) or answer.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ── Graph construction ─────────────────────────────────────────────────────────

def build_graph():
    """
    Build and compile the Optimus LangGraph agent.

    Nodes
    -----
    call_llm   : LLM reasoning step — decides to call a tool or produce final answer
    call_tools : ToolNode that executes whichever tool the LLM requested

    Edges
    -----
    START      → call_llm   (entry point)
    call_llm   → call_tools (when AIMessage has tool_calls)
    call_llm   → END        (when AIMessage is a plain text response)
    call_tools → call_llm   (feed tool result back for next reasoning step)
    """
    graph = StateGraph(AgentState)

    graph.add_node("call_llm", call_llm)
    graph.add_node("call_tools", ToolNode(tools=ALL_TOOLS))

    graph.set_entry_point("call_llm")

    # tools_condition returns "tools" or END; map "tools" to our node name
    graph.add_conditional_edges(
        "call_llm",
        tools_condition,
        {"tools": "call_tools", END: END},
    )

    # After tool execution, loop back to the LLM for the next reasoning step
    graph.add_edge("call_tools", "call_llm")

    return graph.compile()


# ── Public helper ─────────────────────────────────────────────────────────────

def run_agent(user_input: str) -> dict:
    """
    Run the agent for a single user query and return the full final state.

    The returned dict has a `messages` key containing every message in the
    conversation, including intermediate tool calls and results — useful for
    displaying agent reasoning in the UI.
    """
    compiled = build_graph()
    return compiled.invoke({"messages": [("human", user_input)]})
