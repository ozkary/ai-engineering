# Architecture Features

## Multi-Agent System (via Google ADK)

Instead of a single monolithic model call, you are demonstrating Agent2Agent (A2A) collaboration and session state orchestration. You have a sequential team of specialized agents:

Data Agent: In charge of dynamic interaction, input ingestion, and validation.

Lab Agent: A specialized tool-operator that acts as the bridge to clinical infrastructure.

Analysis Agent: A guardrailed clinical communicator translating metrics into safe, empathetic patient insights.

## Model Context Protocol (MCP) Tool Integration
Your project highlights the bleeding edge of agentic connectivity. By hosting your XGBoost/classification heart disease risk model as an MCP Server, you are showing how to decouple the core reasoning engine (Gemini) from specialized, private inference execution environments. The Lab Agent securely invokes this model via standard MCP tool-calling semantics.

## Agent Skills (Custom Tools & Browser APIs)
You are demonstrating core agent agility by equipping your agents with specific "skills":

Bi-directional State Sync (UI Skill): Leveraging ADK's context-syncing capability to dynamically govern a frontend chat window based on the agent's real-time internal state.

Voice-to-Text Transcription Skill: Integrating browser-native Web Speech API utilities, allowing the Data Agent to ingest and cleanly parse unstructured vocal streams into type-safe parameters.

Algorithmic Computation Skill: Real-time BMI processing mathematical calculation fallbacks when raw height and weight are provided instead of a pre-computed BMI float.

## Security, Privacy & Compliance Features
"Agent for Good" requires production-grade guardrails, which you are implementing on both the data and communication fronts:

Zero-PII Compliance: An architectural guarantee that zero Personally Identifiable Information is requested, captured, or stored in the ADK ToolContext.state data bus.

Medical Guardrail Protocol: The Analysis Agent is constrained by strict systemic instructions to append formal medical disclaimers, ensuring the agent operates as a statistical risk analyzer and not a diagnosing physician.

API Key Isolation: Isolating the Google ADK execution blocks completely inside secure Firebase Cloud Functions rather than exposing critical development keys within client-side React bundles.