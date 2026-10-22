import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            result = await session.initialize()
            print("Negotiated MCP protocol version:", result.protocolVersion)
            print("Server name:", result.serverInfo.name)
            print("Server version:", result.serverInfo.version)


if __name__ == "__main__":
    asyncio.run(main())
