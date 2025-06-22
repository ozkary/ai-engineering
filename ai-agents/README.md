# 🏭 Manufacturing AI Agent

This project demonstrates how to build a lightweight AI-powered agent using **LangChain** and **Gemini (Google Generative AI)** to analyze manufacturing sensor data. The agent simulates a control chart analyst that evaluates whether a process is operating within statistical limits, detects SPC (Statistical Process Control) violations, and produces structured reasoning outputs.

The system applies short-term memory to reference previous measurements, assess patterns (e.g., trends, limit violations), and recommend next actions such as continuing to monitor or notifying a supervisor.

---

## 📦 Installation

Set up a virtual environment using Pipenv:

```bash
pipenv shell
pipenv install langchain langchain-google-genai
```

## LangGraph Control Chart Agent

This project implements a **stateful AI agent** using LangGraph for monitoring manufacturing sensor data via Statistical Process Control (SPC) logic. The agent evaluates telemetry patterns (e.g. value spikes, trend reversals) and returns structured insights. This version builds upon the original LangChain script by introducing **modular graph orchestration, improved memory handling**, and **clean execution flow** for production-readiness.

---

## 📦 Installation

Set up your environment using Pipenv:

```bash
pipenv shell
pipenv install langgraph langchain langchain-google-genai python-dotenv
```

## 🔍 Improvements Over LangChain-Only Script

| Feature              | LangChain Script               | LangGraph Agent Version                        |
|----------------------|--------------------------------|------------------------------------------------|
| 🔄 Flow Control       | Linear, procedural flow        | Modular, reactive graph orchestration          |
| 🧠 Memory Scope       | Short-term buffer only         | Flexible integration of multi-node memory      |
| 🛠️ Extendability     | Manual chaining of logic        | Add conditional branches or tools declaratively |
| ⚙️ Orchestration      | Imperative function logic       | Structured, state-based execution flow         |
| 🧪 Reusability        | Harder to modularize            | Each node reusable and testable in isolation   |
