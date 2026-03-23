# agent.py
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_agent():
    # 1. Setup Model (Gemini 2.5 Flash is fast & free)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # 2. Setup Tools
    search_tool = TavilySearchResults(max_results=3)
    tools = [search_tool]

    # 3. Create Agent (The LangGraph way)
    # This returns a CompiledGraph, not an AgentExecutor
    graph = create_agent(llm, tools=tools)

    return graph
