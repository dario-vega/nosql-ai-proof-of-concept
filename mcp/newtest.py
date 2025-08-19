import asyncio
from fastmcp import Client

client = Client("nosqltools-mcp-server.py")

async def call_tool(name: str):
  async with client:
    result = await client.call_tool('list_nosql_tables', {"compartment_name": name})
    print(result)

asyncio.run(call_tool("davega"))