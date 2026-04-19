# backend.py

import os

from langgraph.graph import StateGraph, START
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.types import interrupt, Command
from dotenv import load_dotenv
import requests

load_dotenv()

ALPHA_KEY = os.getenv("ALPHA_KEY")  # Replace with your actual Alpha Vantage API key

# -------------------
# LLM
# -------------------

llm = ChatOllama(model="llama3.2", temperature=0)

# -------------------
# Tools
# -------------------
@tool
def get_stock_price(symbol: str) -> dict:
    """Fetch latest stock price for a given symbol."""
    
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_KEY}"
    )
    r = requests.get(url)
    return r.json()

@tool
def purchase_stock(symbol: str, quantity: int) -> dict:
    """Purchase a given quantity of shares for the specified stock symbol. Requires human approval."""
    decision = interrupt(f"Approve buying {quantity} shares of {symbol}? (yes/no)")

    if isinstance(decision, str) and decision.lower() == "yes":
        return {
            "status": "success",
            "message": f"Purchased {quantity} shares of {symbol}",
        }
    else:
        return {
            "status": "cancelled",
            "message": f"Purchase cancelled for {symbol}",
        }


tools = [get_stock_price, purchase_stock]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# Nodes
# -------------------
def chat_node(state: ChatState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# Graph
# -------------------
memory = MemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=memory)

# -------------------
# FUNCTION FOR STREAMLIT
# -------------------
def run_chat(user_input, thread_id="streamlit-thread", resume=None):
    """
    Handles both normal chat and HITL resume
    """
    if resume:
        result = chatbot.invoke(
            Command(resume=resume),
            config={"configurable": {"thread_id": thread_id}},
        )
    else:
        state = {"messages": [HumanMessage(content=user_input)]}
        result = chatbot.invoke(
            state,
            config={"configurable": {"thread_id": thread_id}},
        )

    return result