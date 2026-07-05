# Specification: MCP Server Integration
## Project: Agent for Good — Model Context Protocol Gateway

### Objective
To layer the Model Context Protocol (MCP) natively into our existing Gen2 Cloud Function endpoint. This enables the Python inference engine to simultaneously act as an HTTP endpoint for the UI and an agent-ready MCP Tool Server for Google ADK orchestrators without launching separate infrastructure.

---

### 1. Protocol Architecture & Transport Layer
* **Unified Coexistence:** The root application route (`api/main.py`) acts as a selective gateway. Standard requests route through Firebase Auth verification, while protocol-handshake streams route directly to the MCP controller.
* **SSE Transport Mechanism:** Because Google Cloud Functions operate as short-lived serverless HTTP environments, the protocol layer must leverage Server-Sent Events (SSE) via the `mcp[cli]` transport spec (`/sse`) rather than standard input/output streams (`stdio`).

---

### 2. Core Dependencies (`requirements.txt`)

To support the protocol layer, append the following libraries to the workspace dependency configuration:

```text
mcp==1.*
uvicorn==0.*
```

### 3. Tool Schema Registration

The machine learning inference routine must be exposed using the FastMCP tool declaration framework inside api/main.py:

- Tool Name: evaluate_heart_risk
- Description Context: "Evaluates a patient's 16-feature lifestyle/demographic matrix and returns a localized XGBoost statistical risk classification."
- Execution Parameters: Binds directly to the pre-existing Pydantic input contract schema (HeartDiseaseFeatures).
- Tool Logic: 1. Accepts the validated data frame payload incoming from the agent context.
   - Executes the underlying predictive model array transformer (predict(data)).
   - Formulates the stratified text tier mapping via the classification array (probability_label(prob)).
   - Returns a flat JSON response packet detailing the structural category tier and raw float scores to the agent state machine.