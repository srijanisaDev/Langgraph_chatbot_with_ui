from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3
import requests
import asyncio
import os
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# -------------------
# 1. LLM
# -------------------
llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.5-flash'
)

# MCP client for local FastMCP server
client = MultiServerMCPClient(
    {
        "arith": {
            "transport" : "stdio",
            "command" : sys.executable,
            "args": ["-u", os.path.join(os.path.dirname(__file__), "main.py")],
            "env": {"MCP_TRANSPORT": "stdio"}
        }
    }
)



class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def build_graph():

    tools = await client.get_tools()

    print(tools) 

    llm_with_tools = llm.bind_tools(tools)



    async def chat_node(state: ChatState):
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    return graph.compile()


async def main():

    chatbot = await build_graph()

    result = await chatbot.ainvoke({"messages" : [HumanMessage(content="Find the divison of 132354 and 23 and give answer like a cricket commentator.")]})

    print(result['messages'][-1].content)


if __name__ == '__main__':
    asyncio.run(main())

