import os
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.tools import load_mcp_tools

from typing import Annotated, List
from typing_extensions import TypedDict

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_KEY')

server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)

# LangGraph state definition
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


async def create_graph(session: ClientSession) -> StateGraph:
    # Load tools from MCP server
    tools = await load_mcp_tools(session)

    # LLM configuration (system prompt can be added later)
    llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=api_key)
    llm_with_tools = llm.bind_tools(tools)

    # Prompt template with user/assistant chat only
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that uses tools to search Wikipedia."),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools

    # Define chat node
    def chat_node(state: State) -> State:
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

    # Build LangGraph with tool routing
    graph = StateGraph(State)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_node", ToolNode(tools=tools))
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition, {
        "tools": "tool_node",
        "__end__": END
    })
    graph.add_edge("tool_node", "chat_node")

    return graph.compile(checkpointer=MemorySaver())


async def list_prompts(session: ClientSession):
    prompt_list = await session.list_prompts()

    if not prompt_list:
        print("No prompts found on the MCP server.")
        return
    
    print("Available Prompts and arguments structure:")
    for prompt in prompt_list:
        print(f"- Prompt Name: {prompt.name}")
        if prompt.args:
            for arg in prompt.args:
                print(f"  - Arg: {arg.name}")
        else:
            print("  - No arguments")

    print("\nUse: /prompt <prompt_name> \"arg1\", \"arg2\", ... to invoke a prompt.")


# Entry point
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            agent = await create_graph(session)
            print("Wikipedia MCP agent is ready.")

            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in {"exit", "quit", "q"}:
                    break

                try:
                    response = await agent.ainvoke(
                        {"messages": user_input},
                        config={"configurable": {"thread_id": "wiki-session"}}
                    )
                    print("AI:", response["messages"][-1].content)
                except Exception as e:
                    print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())