import os
from typing import Annotated, List, TypedDict, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import json
import warnings

from langgraph.graph.message import add_messages

# Suppress the DuckDuckGo search warning
warnings.filterwarnings("ignore", category=RuntimeWarning, module="langchain_community.utilities.duckduckgo_search")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    research_data: str
    account_plan: str
    company_name: str

# System prompt
SYSTEM_PROMPT = """You are an expert Company Research Assistant. Your goal is to help the user create an Account Plan for a target company.
You have access to a search tool.

Process:
1. Identify the company the user wants to research.
2. Conduct research using the search tool. You can perform multiple searches.
3. If you find conflicting info or need guidance, ask the user.
4. Once you have enough info, generate a structured Account Plan.
5. The Account Plan should include: Company Overview, Financials, Key Stakeholders, Pain Points, and Strategic Opportunities.
6. If the user asks to update a section, modify the plan accordingly.

Always be professional and concise.
"""

def create_agent_graph():
    # Initialize tools
    search_tool = DuckDuckGoSearchRun()

    # Initialize LLM inside the function to ensure env vars are set
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

    def agent_node(state: AgentState):
        messages = state['messages']
        # Add system prompt if it's the first message (or handle via system message in history)
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools([search_tool])
        
        # Call LLM
        response = llm_with_tools.invoke(messages)
        
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last_message = state['messages'][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode([search_tool]))

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )

    workflow.add_edge("tools", "agent")

    # Compile the graph
    return workflow.compile()
