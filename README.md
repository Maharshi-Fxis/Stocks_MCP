# Alpha Vantage MCP Server
A Model Context Protocol (MCP) server that provides real-time access to financial market data through the free [Alpha Vantage API](https://www.alphavantage.co/documentation/). This server implements a standardized interface for retrieving stock quotes and company information.



# Features

- Real-time stock quotes with price, volume, and change data
- Detailed company information including sector, industry, and market cap
- Real-time cryptocurrency exchange rates with bid/ask prices
- Daily, weekly, and monthly cryptocurrency time series data
- Historical options chain data with advanced filtering and sorting
- Built-in error handling and rate limit management

## Installation

### Using Claude Desktop


- Clone the repository and build a local image to be utilized by your Claude desktop client

- Change your `claude_desktop_config.json` to match the following, replacing `REPLACE_API_KEY` with your actual key:

 > `claude_desktop_config.json` path
 >
 > - On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
 > - On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "alphavantage": {
			"command": "python",
			"args": [
				"-m",
				"alpha_vantage_mcp.server",
				"run",
				"server.py"
			],
			"env": {
				"ALPHA_VANTAGE_API_KEY": "insert_your_alpha_api_key",
				"PYTHONPATH": "Path to the server.py"
			}
		}
  }
}
```


        
</details>

#### Install packages

```
uv add -r requiremets.txt .
```

#### Running

After connecting Claude client with the MCP tool via json file and installing the packages, Claude should see the server's mcp tools:

You can run the sever yourself via:
In alpha-vantage-mcp repo: 
```
uv run src/alpha_vantage_mcp/server.py
```

## Available Tools

The server implements eight tools:
- `get-stock-quote`: Get the latest stock quote for a specific company
- `get-company-info`: Get stock-related information for a specific company
- `get-time-series`: Get historical daily price data for a stock
- `get-historical-options`: Get historical options chain data with sorting capabilities
- `get-crypto-exchange-rate`: Get current cryptocurrency exchange rates
- `get-crypto-daily`: Get daily time series data for a cryptocurrency
- `get-crypto-weekly`: Get weekly time series data for a cryptocurrency
- `get-crypto-monthly`: Get monthly time series data for a cryptocurrency


## requirements

- Python 3.12 or higher
- httpx
- mcp
