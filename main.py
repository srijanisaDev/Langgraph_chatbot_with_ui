from __future__ import annotations

import os
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("arith")


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "server": "arith"})


def _as_number(x):
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        return float(x.strip())
    raise TypeError("Expected a number (int/float or numeric string)")


@mcp.tool()
async def add(a: float, b: float) -> float:
    """Return a + b."""
    return _as_number(a) + _as_number(b)


@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Return a - b."""
    return _as_number(a) - _as_number(b)


@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Return a * b."""
    return _as_number(a) * _as_number(b)


@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Return a / b."""
    a = _as_number(a)
    b = _as_number(b)
    if b == 0:
        raise ZeroDivisionError("Division by zero")
    return a / b


@mcp.tool()
async def power(a: float, b: float) -> float:
    """Return a ** b."""
    return _as_number(a) ** _as_number(b)


@mcp.tool()
async def modulus(a: float, b: float) -> float:
    """Return a % b."""
    a = _as_number(a)
    b = _as_number(b)
    if b == 0:
        raise ZeroDivisionError("Division by zero")
    return a % b


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "streamable-http").strip().lower()

    if transport not in {"stdio", "http", "sse", "streamable-http"}:
        raise ValueError(
            "Invalid MCP_TRANSPORT. Use one of: stdio, http, sse, streamable-http"
        )

    if transport == "stdio":
        mcp.run(transport="stdio")
        return

    host = os.getenv("MCP_HOST", "127.0.0.1").strip()
    port = int(os.getenv("MCP_PORT", "8000"))
    path = os.getenv("MCP_PATH", "/mcp").strip() or "/mcp"

    mcp.run(
        transport=transport,
        host=host,
        port=port,
        path=path,
    )


if __name__ == "__main__":
    main()
