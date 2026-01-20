import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode
from .agent_state import State


load_dotenv()
api_key = os.getenv("API_KEY")

async def create_graph(session):
    # connect to mcp server exposed tools
    tools = await load_mcp_tools(session)

    openai_instance = ChatOpenAI(
        model='gpt-4',
        temperature=0,
        api_key=api_key
    )

    llm_with_tools = openai_instance.bind_tools(tools)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that uses tools to search Wikipedia"),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools

    def chat_node(state: State) -> State:
        pass

