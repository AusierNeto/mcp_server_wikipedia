from mcp import ClientSession, StdioServerParameters

# MCP Client can start the server
server_params = StdioServerParameters(
    command=["python"],
    args=["mcp_server.py"]
)

