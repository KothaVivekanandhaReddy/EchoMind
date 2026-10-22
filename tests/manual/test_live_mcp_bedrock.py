import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            cases = [
                (
                    "Explicit commitment",
                    "I promised to finish the evaluation by Friday.",
                ),
                (
                    "Ambiguous intention",
                    "I should finish the evaluation.",
                ),
                (
                    "Negated commitment",
                    "I did not promise to finish the evaluation.",
                ),
            ]

            for label, text in cases:
                print(f"\n--- {label} ---")
                result = await session.call_tool(
                    "remember_from_text",
                    arguments={"text": text},
                )

                if result.isError:
                    print("MCP tool returned an error.")
                for item in result.content:
                    if hasattr(item, "text"):
                        print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
