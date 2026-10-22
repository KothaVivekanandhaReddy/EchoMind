
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def result_data(result) -> dict:
    """Extract a dictionary returned by an MCP tool."""
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

            # 1. Save a commitment and its original evidence.
            saved_result = await session.call_tool(
                "remember_memory",
                {
                    "memory_type": "commitment",
                    "content": "Submit the EchoMind hackathon project",
                    "source_id": "mcp_demo_001",
                    "source_text": (
                        "I promised to submit the EchoMind hackathon "
                        "project by Friday."
                    ),
                },
            )
            saved = result_data(saved_result)
            assert saved["saved"] is True
            memory_id = saved["memory_id"]
            print("1. Memory saved:", memory_id)

            # 2. Search for the commitment.
            search_result = await session.call_tool(
                "search_memory",
                {
                    "query": "What did I promise to submit?",
                    "memory_type": "commitment",
                    "limit": 5,
                },
            )
            search = result_data(search_result)
            assert search["found"] is True
            assert any(
                item["memory_id"] == memory_id
                for item in search["results"]
            )
            print("2. Search found the saved commitment.")

            # 3. Retrieve its original supporting evidence.
            evidence_result = await session.call_tool(
                "get_memory_evidence",
                {"memory_id": memory_id},
            )
            evidence = result_data(evidence_result)

            assert evidence["found"] is True
            assert evidence["evidence_available"] is True
            assert "by Friday" in evidence["evidence"]

            print("3. Original source evidence retrieved.")
            print("Evidence:", evidence["evidence"])
            print("\nEnd-to-end MCP tool test passed.")


if __name__ == "__main__":
    asyncio.run(main())
