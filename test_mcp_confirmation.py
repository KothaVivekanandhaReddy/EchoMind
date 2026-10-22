
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

            # Explicit commitment: save.
            result = await session.call_tool(
                "remember_from_text",
                {"text": "I promised to finish the evaluation by Friday."},
            )
            saved = result_data(result)
            assert saved["action"] == "save"
            assert saved["saved"] is True
            print("Explicit commitment: saved.")

            # Ambiguous intention: ask for confirmation, don't save.
            result = await session.call_tool(
                "remember_from_text",
                {"text": "I should finish the evaluation."},
            )
            confirmation = result_data(result)
            assert confirmation["action"] == "confirm"
            assert confirmation["saved"] is False
            print("Ambiguous intention: confirmation requested.")

            # Negated commitment: ignore.
            result = await session.call_tool(
                "remember_from_text",
                {"text": "I didn't promise to finish the evaluation."},
            )
            ignored = result_data(result)
            assert ignored["action"] == "ignore"
            assert ignored["saved"] is False
            print("Negated statement: ignored.")

            print("MCP confirmation-policy tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
