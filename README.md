# ERPNext MCP Server

Connects ERPNext to any MCP client (Claude Desktop, MCP Inspector, etc.). Query live ERP data: invoices, stock, customers, sales through natural language.

## Demo
[Screen recording link here]

## Architecture

```
MCP Client (Claude Desktop / MCP Inspector)
        |
        | JSON-RPC over stdio
        v
MCP Server (Python + fastmcp 3.4.2)
        |
        | HTTP REST API
        v
ERPNext v16 (Docker — localhost:8080)
```

## Prerequisites

- Python 3.11+
- Docker Desktop
- Node.js (for MCP Inspector)
- (Optional) Claude Desktop, the server works with any MCP client

## 1. ERPNext Setup

```bash
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker
docker compose -f pwd.yml up -d
```

Wait for containers to start (~15 minutes first time). Open `http://localhost:8080` and login with `Administrator / admin`.

Generate API credentials:
- Go to **My Settings → API Access → Generate Keys**
- Copy the **API Key** and **API Secret**

> After a PC restart, run `docker compose -f pwd.yml start` (not `up`) to resume containers without reinstalling.

## 2. MCP Server Setup

```bash
git clone https://github.com/YOUR_USERNAME/erpnext-mcp-server.git
cd erpnext-mcp-server
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the root folder:

```
ERPNEXT_URL=http://localhost:8080
ERPNEXT_API_KEY=your_api_key_here
ERPNEXT_API_SECRET=your_api_secret_here
```

## 3. Claude Desktop Configuration

Open `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "erpnext": {
      "command": "C:\\path\\to\\erpnext-mcp-server\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\erpnext-mcp-server\\server.py"],
      "env": {
        "ERPNEXT_URL": "http://localhost:8080",
        "ERPNEXT_API_KEY": "your_key",
        "ERPNEXT_API_SECRET": "your_secret"
      }
    }
  }
}
```

Fully quit Claude Desktop (system tray → Quit) and reopen. The tools icon in chat will show 5 ERPNext tools ready to use.

## 4. Local Testing with MCP Inspector

To test without Claude Desktop, use MCP Inspector:

```bash
# Install Node.js first if not available
# Then run:
npx @modelcontextprotocol/inspector python server.py
```

Open the URL printed in terminal. Click **Connect** → **Tools** tab to see and run all 5 tools interactively.

## Available Tools

`get_outstanding_invoices` Fetch unpaid, partly paid, or overdue sales invoices 
`create_customer`  Create a new customer record in ERPNext 
`get_stock_summary`  Current stock levels across warehouses 
`search_products`  Search the item catalog by name 
`get_sales_report` Sales summary between two dates 

## Project Structure

```
erpnext-mcp-server/
├── server.py            # MCP server (all 5 tools defined here)
├── erpnext_client.py    # ERPNext REST API client wrapper
├── .env                 # API credentials (not committed to git)
├── .gitignore
├── requirements.txt
└── README.md
```

## Tech Stack
Python + fastmcp 3.4.2 -> MCP server framework 
ERPNext v16 via Docker -> Self-hosted ERP (frappe_docker) 
httpx -> HTTP client for ERPNext REST API 
python-dotenv -> Environment variable management 
Claude Desktop / MCP Inspector -> MCP client for testing 