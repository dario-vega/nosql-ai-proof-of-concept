# NoSQL-tools MCP Server (nosqltools-mcp-server.py)

A Python-based MCP (Model Context Protocol) server that provides a suite of tools for managing and interacting with NoSQL tables. 
This MCP server is intented to be used  as a proof of concept for exploring models using MCP Servers.
It is based on https://github.com/oracle/mcp

## Overview

nosqltools-mcp-server.py is a FastMCP-based server that provides various tools for managing OCI NoSQL resources with SQL execution capabilities.

## Features

- **Compartment Management**
  - List all compartments
  - Get compartment by name

- **NoSQL Operations**
  - List  NoSQL Tables in specific compartments
  - Describe  NoSQL Tables in specific compartments
  - Execute SQL queries specific compartments

## Prerequisites

- Python 3.x
- fastmcp (installed automatically via requirements.txt)
- OCI SDK (installed via requirements.txt)
- NoSQL SDK - Borneo (installed via requirements.txt)
- Valid OCI configuration file with credentials

## Installation

1. Clone this repository.
2. Install required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
   This will install `oci`, `requests`, `fastmcp`, `borneo` and all other dependencies.
3. Set up your OCI config file at ~/.oci/config

## OCI Configuration

The server requires a valid OCI config file with proper credentials. 
The default location is ~/.oci/config. For instructions on setting up this file, 
see the [OCI SDK documentation](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm).

## Required Python Packages

- oci
- borneo
- requests
- fastmcp


## MCP Server Configuration
Installation is dependent on the MCP Client being used, it usually consists of adding the MCP Server invocation in a json config file, for example with Claude UI on windows it looks like this:
```
{
  "mcpServers": {
    "dbtools": {
      "command": "C:\\Python\\python.exe",
      "args": [
        "C:\\Users\\user1\\nosql-ai-proof-of-concept\nosqltools-mcp-server.py"
      ]
    }
  }
}
```


## Usage

The server runs using stdio transport and can be started by running:

```
fastmcp run nosqltools-mcp-server.py:mcp
```

## API Tools

You can use MCP inspector to explore the API Tools provided

The [MCP Inspector](https://modelcontextprotocol.io/legacy/tools/inspector)  is an interactive developer tool for testing and debugging MCP servers. 


## Security

The server uses OCI's built-in authentication and authorization mechanisms, including:
- OCI config file-based authentication
- Signer-based authentication for specific endpoints

## Example Prompts

Here are example prompts you can use to interact with the MCP server, this test was deployed using Claude Desktop.
see https://modelcontextprotocol.io/quickstart/user

```
"There’s an MCP server named nosqltools"
"List all tables in davega compartment"
"Please let me view the first 20 lines in the table called sessiontable"
"Can you provide me those data as a table"
"Can you provide me those data in JSON format"
"can you read the data in the table AgentInventoryEntity"
"What about the data in test_ddb_complex"

```
