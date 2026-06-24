# AI Agents with Google ADK: Technical Bootstrap Blueprint

Welcome to the foundational training ground for the Google Agent Development Kit (ADK). If you have ever looked at production-grade agentic frameworks and felt overwhelmed by massive abstractions, complex multi-agent synchronization code, or brittle state loops, this project is designed for you. 

This repository provides a **shallow-curve, step-by-step curriculum** focused on building confidence with intelligent software systems using the native **Google ADK**. 

---

## 🧭 Educational Philosophy: Progressive Evolution & True Reusability

Our core mission is to introduce you to the Google ADK starting with its absolute **basic core concepts** and progressively improving your agents' capabilities line by line.

A major flaw in many Python-based AI tutorials is that they treat agents as throwaway scripts, leading to massive code duplication. This project rejects that pattern by focusing heavily on **Software Engineering Reusability**. 

![ozkary Agent Development Kit - ADK](../images/ozkary-agent-development-kit-architecture-md.jpg)

By leveraging Python's module system alongside the Google ADK's fluid configuration layer, you will see exactly how to build enterprise-ready agents that are modular, extensible, and completely DRY (Don't Repeat Yourself).

## Project Architecture

This workspace consolidates its package management at the root level while keeping individual agent directories self-contained with their own isolated local runtime parameters.

```
adk/
│
├── tools/                    # SHARED INTEGRATIONS ENGINE and TOOLS
│   ├── __init__.py           # Exposes reusable business logic
│   └── custom_tools.py       # Centralized @mcp.tool or FunctionTool definitions
│
├── basic_agent/              # STEP 1: Core Fundamentals (Model + Instructions)
│   ├── __init__.py           # Exports basic_agent as the active 'agent'
│   ├── .env                  # Sandbox environment keys & credentials
│   └── agent.py              # Baseline intelligence wrapper
│
├── tool_agent/               # STEP 2: The Action Loop (Action & Interaction)
│   ├── __init__.py           # Exports tool_agent as the active 'agent'
│   ├── .env                  # Sandbox environment keys & credentials
│   └── agent.py              # IMPORTS basic_agent & attaches services
│
└── memory_agent/             # STEP 3: Memory persistent
    ├── __init__.py           # Exports memory_agent as the active 'agent'
    ├── .env                  # Sandbox environment keys & credentials
    └── agent.py              # IMPORTS memory_agent & enforces strict Pydantic parsing
```

## 🛠️ Environment Setup & Centralized Installation

To eliminate dependency version conflicts and ensure lightning-fast execution, the entire workspace runtime footprint is isolated within a modern, unified virtual environment managed by **`uv`** at the repository root.

### Prerequisites
Ensure you have the high-performance Rust-backed package manager **`uv`** installed globally on your workstation:

```bash
# Install uv globally (macOS/Linux)
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Install uv globally (Windows PowerShell)
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```

### Quick Start Installation

# 1. Clone the repository and navigate to the root directory
git clone [https://github.com/ozkary/ai-engineering.git](https://github.com/ozkary/ai-engineering.git)
cd ai-engineering

# 2. Initialize and synchronize the unified environment using our Makefile
make setup

# 3. Configure your local .env file in the root directory to map your Google Cloud credentials
```bash
cat << EOF > .env
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/gcp-service-account.json"
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GEMINI_LOCATION="us-east1"
EOF
```

## Launching the Interactive Developer UI (adk web)

## 📡 Launching the Interactive Developer UI

 `uv run` handles loading your environment parameters on the fly without requiring an activated subshell.

Before launching, you can run static quality enforcement directly via the automated linter array:

> The Makefile defines commands which are used as shortcuts to execute devops operations

```bash
# Run structural checks and linting across the codebase via Ruff
make lint
```
> Run the interactive dev web tool

```bash
# Step into your Python ADK project folder
cd adk

# Run the basic agent sandbox cleanly
make run-basic

# Run the tool agent sandbox cleanly
make run-tool

# Run the persisted memory agent
make run-memory


```
Open the resulting local network loopback link printed in your terminal window (typically http://localhost:8000) to interact with your progressively evolving agent live!

