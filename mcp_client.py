import asyncio
import pip_system_certs.wrapt_requests

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from client.openai_agent_graph import create_graph

# MCP Client can start the server
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            agent = await create_graph(session)
            print("Wikipedia Agent is Ready")

            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in {"exit", "quit", "q"}:
                    break

                print(user_input)
                try:
                    response = await agent.ainvoke(
                        {"messages": user_input},
                        config={"configurable": {"thread_id": "wiki-session"}}
                    )
                    print("Agent:", response["messages"][-1].content)
                except Exception as e:
                    print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
    
