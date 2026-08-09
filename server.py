"""MCP server exposing the research assistant as a single callable tool.

Run with:  python server.py  (communicates over stdio)
"""

from mcp.server.fastmcp import FastMCP

from agentic_crew import run

mcp = FastMCP("agentic_research_assistant")


@mcp.tool()
async def research(query: str) -> str:
    """Plan and run the multi-agent research workflow for a query.

    Args:
        query: The research question or request.

    Returns:
        The final synthesized research output.
    """
    result = run(query)
    return str(result) if result else "No results returned"


if __name__ == "__main__":
    mcp.run(transport="stdio")
