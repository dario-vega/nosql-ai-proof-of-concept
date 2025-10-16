# NoSQL-tools MCP Server (`nosqltools-mcp-server.py`)

## 🚧 CAUTION & DISCLAIMER

> **Not for Production — For Experimental/Education Use Only**
>
> This MCP server interacts with OCI NoSQL resources and can expose, modify, or delete data.  
> **You are solely responsible for correct setup, permissions, and data security.**
>
> - **DO NOT USE with production data or environments.**
> - **No guarantee of data privacy or regulatory compliance** (GDPR, CCPA, etc.).
> - **Review, audit, and sanitize all activity and results.**
> - Before using any third-party tools/scripts (like `anonimizer*.py`), ensure they meet your legal, privacy, and security standards.
>
> *No warranty is provided. Use at your own risk and in accordance with your organization's legal, security, and privacy policies.*

---

## Why Use This Tool?

This project enables hands-on exploration of AI and NoSQL data workflows using the Model Context Protocol (MCP), such as rapid prototyping, learning, and proof-of-concept demos.  
**Experiments with private, compliance-approved LLMs can unlock powerful automation and data insights—provided you follow responsible security and privacy practices.**

---

## Key Risks and Security Practices

### ⚠️ AI & LLM Data Exposure Warning

- **LLMs may inadvertently reveal or retain any data you provide—including confidential or sensitive data.**
- **Never connect LLMs to production data.** Use only masked/sanitized test data for experimentation.
- Prefer **private LLMs** (deployed within your own organization) to minimize data risk and maximize compliance and control.
- **Consult with your compliance and security teams before enabling LLM-based workflows for any business data.**

### Security Quick Checklist

- Use least-privilege OCI accounts and assign only necessary permissions.
- Regularly review and audit logs, outputs, and queries for privacy breaches or anomalies.
- Carefully vet all external dependencies (libraries, scripts, anonymization tools) for security, privacy, and licensing before use with sensitive information.
- The included anonymizer script (`anonimizer*.py`) is a demonstration only—**thoroughly review and adapt before use; it does not guarantee compliance or full anonymization.**

---

## Features

- Compartment management: List and retrieve compartments.
- NoSQL operations: List, describe, and query NoSQL tables.
- Built-in SQL guardrails for safer experimentation.

---

## Intended Use

This repository is a **proof of concept** for integrating MCP servers with OCI NoSQL.  
It is intended exclusively for local experimentation, technical exploration, and demonstrations.  
**Never use with production data or environments.**

---

## Prerequisites

- Python 3.x
- [`fastmcp`](https://github.com/ModelContextProtocol/fastmcp/) (via `requirements.txt`)
- [OCI Python SDK (`oci`)](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm)
- [NoSQL SDK (Borneo)](https://docs.oracle.com/en/database/other-databases/nosql-database/25.1/java-driver/index.html)
- OCI credentials/config file

---

## Installation & Setup

1. **Clone the repository and install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

2. **Set up your OCI configuration**
    - Edit `~/.oci/config` as described in the OCI SDK documentation.

---

## MCP Server Configuration

Register the server with your MCP client.  
Example JSON entry for Claude UI on Windows:

```json
{
  "mcpServers": {
    "dbtools": {
      "command": "C:\\Python\\python.exe",
      "args": [
        "C:\\Users\\user1\\nosql-ai-proof-of-concept\\nosqltools-mcp-server.py"
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



## Example Prompts

You can use prompts such as: 

```
"There’s an MCP server named nosqltools"
"List all tables in davega compartment"
"Please let me view the first 20 lines in the table called sessiontable"
"Can you provide me those data as a table"
"Can you provide me those data in JSON format"
"can you read the data in the table AgentInventoryEntity"
"What about the data in test_ddb_complex"
```

This project has been tested with MCP-compatible clients such as Claude Desktop.
See https://modelcontextprotocol.io/quickstart/user  for more examples.

## Further Guidance 
- When using anonymization scripts, always manually review outputs for adequacy and compliance.
- In regulated or sensitive environments, always consult with your legal, privacy, and compliance teams before deploying, adapting, or integrating any LLM- or AI-based workflow with your data or systems.
- For important business automation or anonymization needs, prefer professionally supported tools rated for enterprise use and compliance.
     
