from mcp import ClientSession, StdioServerParameters


server_params = StdioServerParameters(
    command=["python"],
    args=["mcp_server.py"]
)

