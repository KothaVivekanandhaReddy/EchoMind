
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def parse_result(result):
    for item in result.content:
        if getattr(item, "text", None):
            return json.loads(item.text)
    raise AssertionError("MCP tool returned no text result")


async def main():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            proposed_text = (
                "I should finish the EchoMind confirmation test."
            )

            proposal = parse_result(
                await session.call_tool(
                    "remember_from_text",
                    {"text": proposed_text},
                )
            )
            assert proposal["action"] == "confirm"
            assert proposal["saved"] is False
            confirmation_id = proposal["confirmation_id"]
            print("Ambiguous intention: pending confirmation created.")

            declined = parse_result(
                await session.call_tool(
                    "confirm_memory",
                    {
                        "confirmation_id": confirmation_id,
                        "confirmed": False,
                    },
                )
            )
            assert declined["saved"] is False
            print("Declined confirmation: no save.")

            reused = parse_result(
                await session.call_tool(
                    "confirm_memory",
                    {
                        "confirmation_id": confirmation_id,
                        "confirmed": True,
                    },
                )
            )
            assert reused["saved"] is False
            print("Resolved confirmation cannot be reused.")

            second_proposal = parse_result(
                await session.call_tool(
                    "remember_from_text",
                    {"text": proposed_text},
                )
            )
            second_id = second_proposal["confirmation_id"]

            accepted = parse_result(
                await session.call_tool(
                    "confirm_memory",
                    {
                        "confirmation_id": second_id,
                        "confirmed": True,
                    },
                )
            )
            assert accepted["saved"] is True
            memory_id = accepted["memory_id"]
            print("Accepted confirmation: saved.")

            evidence = parse_result(
                await session.call_tool(
                    "get_memory_evidence",
                    {"memory_id": memory_id},
                )
            )
            assert evidence["found"] is True
            assert evidence["evidence"] == proposed_text
            print("Source evidence: retrieved and verified.")

            print("MCP pending-confirmation tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
