from typing import Any, List, Dict, Optional
import asyncio
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import os

from .tools import (
    make_alpha_request,
    format_quote,
    format_company_info,
    format_time_series,
    format_historical_options,
    ALPHA_VANTAGE_BASE,
    API_KEY
)

if not API_KEY:
    raise ValueError("Missing ALPHA_VANTAGE_API_KEY environment variable")

server = Server("alpha_vantage_finance")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    
    return [
        types.Tool(
            name="get-stock-quote",
            description="Get current stock quote information",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-company-info",
            description="Get detailed company information",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-time-series",
            description="Get daily time series data for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                    "outputsize": {
                        "type": "string",
                        "description": "compact (latest 100 data points) or full (up to 20 years of data)",
                        "enum": ["compact", "full"],
                        "default": "compact"
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-historical-options",
            description="get historical options chain data for a stock with sorting capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                    "date":{
                        "type": "string",
                        "description": "Optional: Trading date in YYYY-MM-DD format (defaults to previous trading day, must be after 2008-01-01)",
                        "pattern": "^20[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional: Number of contracts to return (default: 10, use -1 for all contracts)",
                        "default": 10,
                        "minimum": -1
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Optional: Field to sort by",
                        "enum": [
                            "strike",
                            "expiration",
                            "volume",
                            "open_interest",
                            "implied_volatility",
                            "delta",
                            "gamma",
                            "theta",
                            "vega"
                            "rho",
                            "last",
                            "bid",
                            "ask"
                        ],
                        "default": "strike"
                    },
                    "sort_order": {
                        "type": "string",
                        "description": "Optional: Sort order",
                        "enum": ["asc", "desc"],
                        "default": "asc"
                    }
                },
                "required": ["symbol"]
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    
    if not arguments:
        return [types.TextContent(type="text", text="Missing arguments for the request")]

    if name == "get-stock-quote":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            quote_data = await make_alpha_request(
                client,
                "GLOBAL_QUOTE",
                symbol
            )

            if isinstance(quote_data, str):
                return [types.TextContent(type="text", text=f"Error: {quote_data}")]

            formatted_quote = format_quote(quote_data)
            quote_text = f"Stock quote for {symbol}:\n\n{formatted_quote}"

            return [types.TextContent(type="text", text=quote_text)]

    elif name == "get-company-info":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            company_data = await make_alpha_request(
                client,
                "OVERVIEW",
                symbol
            )

            if isinstance(company_data, str):
                return [types.TextContent(type="text", text=f"Error: {company_data}")]

            formatted_info = format_company_info(company_data)
            info_text = f"Company information for {symbol}:\n\n{formatted_info}"

            return [types.TextContent(type="text", text=info_text)]

    elif name == "get-time-series":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()
        outputsize = arguments.get("outputsize", "compact")

        async with httpx.AsyncClient() as client:
            time_series_data = await make_alpha_request(
                client,
                "TIME_SERIES_DAILY",
                symbol,
                {"outputsize": outputsize}
            )

            if isinstance(time_series_data, str):
                return [types.TextContent(type="text", text=f"Error: {time_series_data}")]

            formatted_series = format_time_series(time_series_data)
            series_text = f"Time series data for {symbol}:\n\n{formatted_series}"

            return [types.TextContent(type="text", text=series_text)]
        
    elif name == "get-historical-options":
        symbol = arguments.get("symbol")
        date = arguments.get("data")
        limit = arguments.get("limit", 10)
        sort_by = arguments.get("sort_by", "strike")
        soret_order = arguments.get("sort_order", "asc")

        if not symbol:
            return [type.TextContent(type="text", text="Missing symbol parameter")]
        
        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            params = {}
            if date:
                params["date"] = date

            options_data = await make_alpha_request(
                client,
                "HISTORICAL_OPTIONS",
                symbol,
                params
            )

            if isinstance(options_data, str):
                return [types.TextContent(type="text", text=f"Error:{options_data}")]
            
            formatted_options = format_historical_options(options_data, limit, sort_by, soret_order)
            options_text = f"Historical options data for {symbol}"
            if date:
                options_text += f" on {date}"
            options_text += f":\n\n{formatted_options}"

            return [types.TextContent(type="text", text=options_text)]

    
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="alpha_vantage_finance",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
