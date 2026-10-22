# EchoMind

EchoMind is a source-grounded personal memory agent. It stores commitments, decisions, preferences, goals, and facts, then retrieves relevant memories with their supporting source evidence.

## Current capabilities

- Store memories in SQLite.
- Search memories by query and optional memory type.
- Retrieve the original evidence supporting a memory.
- Classify natural-language input before saving it.
- Request confirmation for ambiguous intentions.
- Reject negated or uncertain statements.
- Use Amazon Bedrock for memory proposals, with deterministic application policy validation.
- Expose memory operations through an MCP server using Streamable HTTP.

## Requirements

- Python 3.12 or compatible Python version.
- AWS credentials configured for an account with access to Amazon Bedrock.
- Access to the configured Bedrock model in your selected AWS Region.

## Setup (Windows PowerShell)

Clone or download this repository, then open PowerShell in the project directory.

Create and activate a virtual environment:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install pytest
```

Configure AWS credentials using your preferred AWS CLI profile or environment configuration. Do not commit credentials or secret files to the repository.

## Run with Amazon Bedrock

Set the provider and model configuration in PowerShell:

```powershell
$env:ECHOMIND_LLM_PROVIDER = "bedrock"
$env:ECHOMIND_BEDROCK_MODEL_ID = "openai.gpt-oss-120b-1:0"
$env:AWS_REGION = "us-east-1"
```

Ensure the configured AWS identity has permission to invoke the selected Bedrock model.

Start the MCP server:

```powershell
python -m echomind.server
```

The Streamable HTTP MCP endpoint is:

`http://127.0.0.1:8000/mcp`

Keep the server running while using an MCP client.

## Run with the rule-based provider

For local development without Bedrock inference, open a new PowerShell session, activate the virtual environment, and run:

```powershell
$env:ECHOMIND_LLM_PROVIDER = "rule_based"
python -m echomind.server
```

## Test the project

Run the core automated test suite:

```powershell
python -m pytest tests -q
```

To inspect the server's tools, start the server and run this command in a second terminal:

```powershell
python .\test_mcp_connection.py
```

The repository also contains standalone integration scripts for memory retrieval, evidence, confirmation handling, and live Bedrock/MCP testing. Review each script before running it; live integration tests may write to the local development database or incur AWS charges.

## MCP tools

The server exposes these tools:

- `remember_memory` — save a memory with source evidence.
- `search_memory` — search memories and return supporting evidence.
- `get_memory_evidence` — retrieve a memory and its evidence.
- `remember_from_text` — classify text and propose a memory where policy allows.
- `confirm_memory` — accept or decline a pending confirmation.

## Data and configuration

The SQLite database is stored under `data/echomind.db` by default. Local data, virtual environments, Python caches, and AWS CLI test artifacts should not be committed.

The Bedrock provider requires valid AWS credentials and model access. The rule-based provider does not require Bedrock inference.

## Current limitations

- Memory search currently uses keyword-based matching.
- A dedicated end-user web interface and voice experience are not yet included in this backend.
- Alexa+ platform integration beyond the self-hosted MCP server has not been established by this repository alone.

