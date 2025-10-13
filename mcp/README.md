# NoSQL-tools MCP Server (`nosqltools-mcp-server.py`)

## ⚠️ CAUTION & DISCLAIMER

> **This repository is intended for proof-of-concept and exploration purposes only.  
> USE AT YOUR OWN RISK.**
>
> - This MCP server interacts directly with your OCI NoSQL resources. If misconfigured or used carelessly, it may expose, modify, or delete sensitive data.
> - Do **not** run against production environments or confidential data.
> - This code does **not** guarantee data privacy or compliance with regulatory standards (such as GDPR, CCPA, etc.) or with your organization’s security policies.
> - **You** are responsible for correct permissions, configuration, and data security.
> - Always use minimum required privileges and review all logs and outcomes.
> - If you use anonymization or data-handling scripts (such as `anonimizer*.py`), review them and their outputs for adequacy and risk.
> - Before using any open-source or third-party tool in this context, confirm it is approved and compliant by your legal, security, and privacy teams.

---

## Overview

`nosqltools-mcp-server.py` is a FastMCP-based MCP server that exposes tools for managing and querying **OCI NoSQL tables** via the [Model Context Protocol (MCP)](https://github.com/oracle/mcp).  
This server is designed for hands-on experimentation and **is not suitable for production use**.

---

## Features

- **Compartment Management**
    - List all compartments
    - Get compartment by name
- **NoSQL Operations**
    - List NoSQL tables in compartments
    - Describe NoSQL tables
    - Execute SQL queries in compartments

---

## Intended Use

This repository serves as a **proof of concept** for integrating MCP servers with OCI NoSQL.  
It is intended for local experimentation, technical exploration, and demonstrations only.

**Do not use this with production data or production environments.**

---

## ⚠️ Exposing Data to LLMs: Risk and Responsibility

If you use this project in conjunction with large language models (LLMs) or AI assistants—whether public, private, or hosted—be aware of the following:

- **Data Exposure Risk:**  
  LLMs may utilize (and potentially retain or reveal) the data you provide, including in model outputs, logs, or interactions.  
  Sensitive data, credentials, personal information, or intellectual property should never be sent to LLMs unless specifically approved.

- **Compliance & Security:**  
  Exposing regulated, confidential, or production data to LLMs can violate privacy laws (GDPR, CCPA, etc.) or your organization's security policies.  
  Always verify what data is sent and what controls are in place for retention, auditing, and access.

- **Best Practices for Integrating LLMs:**  
    - **Minimize Data:**  Send only the minimum necessary context to LLMs.
    - **Mask/Anonymize:**  Use strict data masking/anonymization prior to submitting data.
    - **Use Private/Approved LLMs:**  Prefer LLMs deployed in private, organization-controlled environments with proper access controls.
    - **Audit and Monitor:**  Track LLM queries and responses for potential leaks or inappropriate data use.
    - **Review Permissions:**  Assign the lowest privileges possible to any LLM data or service account.
    - **Do Not Connect to Production:**  Never connect LLMs directly to production data sources.

- **Ultimate Responsibility:**  
  It is the user’s responsibility to ensure no sensitive or unauthorized data is exposed to LLMs as a result of using, adapting, or extending this project.

For guidance, consult your privacy, legal, and security teams before integrating any LLMs or AI-driven tools with your data or systems.

## Security & Compliance Considerations

- **Principle of Least Privilege:**  
  Grant only the minimal required permissions for the service account.
- **Avoid Production Data/Environments:**  
  Never use production or non-sanitized data for testing or demos.
- **Monitor & Audit Usage:**  
  Monitor server operations, review logs, and audit for anomalies or unauthorized activities.
- **Sanitize Outputs:**  
  When sharing query results or log files, ensure all sensitive information is properly anonymized.  
  The provided anonymizer scripts (`anonimizer*.py`) are for demonstration only—**review and adapt before use**.
- **External Dependencies:**  
  This repository uses open-source and third-party libraries (e.g., MCP, FastMCP, Faker, OCI, Borneo).  
  **You are responsible** for ensuring third-party tools used are security- and compliance-approved.

---

## Open Source, Third-party, and Professional Tools

- **Open-source libraries** such as [Faker](https://faker.readthedocs.io/), [Mimesis](https://mimesis.name/), [anonypy](https://github.com/tolstoyevsky/anonypy) may help with data anonymization, but **must be vetted** for licensing, security, and compliance prior to use with sensitive data.
- For higher-stakes environments or requirements, choose **professionally supported/enterprise data masking and anonymization solutions** as recommended by your organization.

---

## Prerequisites

- Python 3.x
- `fastmcp` (installed via `requirements.txt`)
- OCI Python SDK (`oci`)
- NoSQL SDK - Borneo
- OCI credentials/config file

---

## Installation

1. **Clone this repository.**
2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up your OCI config:**  
   The default file is `~/.oci/config`. See [OCI SDK documentation](https://docs.oracle.com/en-us/iaas/tools/python/latest/) for details.

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
