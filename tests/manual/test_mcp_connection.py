
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()

            print("MCP connection successful.")
            print("Available tools:")

            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
