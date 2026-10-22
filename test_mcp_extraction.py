
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def result_data(result) -> dict:
    if result.isError:
        raise RuntimeError(f"MCP tool failed: {result.content}")

    if result.structuredContent:
        return result.structuredContent

    for item in result.content:
        if getattr(item, "type", None) == "text":
            return json.loads(item.text)

    raise RuntimeError("MCP tool returned no readable result.")


async def main():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Explicit commitment should be extracted and saved.
            result = await session.call_tool(
                "remember_from_text",
                {
                    "text": (
                        "I promised to finish the RAG evaluation "
                        "by Friday."
                    )
                },
            )
            saved = result_data(result)

            assert saved["saved"] is True
            assert saved["type"] == "commitment"
            assert "RAG evaluation" in saved["content"]
            assert "by Friday" in saved["evidence"]

            print("Extracted and saved:", saved["content"])
            print("Evidence:", saved["evidence"])

            # Unsupported text should not be saved.
            result = await session.call_tool(
                "remember_from_text",
                {"text": "The weather is nice today."},
            )
            ignored = result_data(result)

            assert ignored["saved"] is False
            assert ignored["reason"] == "no_supported_memory"

            print("Unsupported text correctly rejected.")
            print("MCP extraction tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
