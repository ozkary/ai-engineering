# Specification: Server-Side ADK Workflow & Agent Governance
## Project: Agent for Good - Structured Cognitive Analysis Layer

### 1. Architectural Architecture & Governance Separation
To keep the primary network layer (`server.ts`) completely decoupled from cognitive operations, all agentic processes are strictly isolated into modular sub-packages.
* **The Proxy Layer (`server.ts`):** Exposes the public-facing endpoint, verifies the incoming network health payload, drops it into the workflow execution runner, and returns the unified JSON block.
* **The Core Workspace (`/src`):** Houses independent modules for structural execution logic, state diagrams, and enterprise compliance rules.

---

### 2. File System Architecture & Component Isolation
To prevent development files from blending code archetypes or going "off the rails," all instances of ADK agent classes must be structurally partitioned into specific files. Components cannot be cross-declared within the orchestration scope.

```bash
/app/server/src
  ├── /workflows
  │    └── heartRiskWorkflow.ts   # PURE ORCHESTRATION: Graph mapping and execution flow ONLY
  ├── /agents
  │    └── analystAgent.ts        # DEFINITIONS FILE: LlmAgent instances, Gemini configurations, schemas
  └── /governance
       └── compliance.ts          # RUNTIMES & RULES: System constraints, Runner, MemoryRunner, disclaimers
```

### 3. ADK State-Graph Workflow Spec (/workflows/heartRiskWorkflow.ts)
The lifecycle of a calculation payload is managed as a strict linear state graph using the ADK Workflow engine. No task can bypass a transition edge. This file acts strictly as an orchestration wrapper and imports its structural components from the definitions packages.

**State Graph Schema**

``` typescript
const root_agent = Workflow(
    name: "hd_analysis_agent",
    edges: [
        (START, parse_request),
        (parse_request, send_mcp_request),
        (send_mcp_request, llm_risk_review),
        (llm_risk_review, send_analysis)
    ]
)
```

### 4. Code Generation Rules for Agents & Models (/agents/analystAgent.ts)

When instantiating node layers, antigravity must adhere strictly to native Google ADK definitions, ensuring explicit resilience handling and type containment.

**Configuration Blueprint**
- Engine Type: LlmAgent
- Model Engine: Native Gemini declarations using explicit fallback retry schemas.
- Output Isolation: Mandatory execution of custom TypeScript schema models mapping strictly to specified output properties.

**Structural Code Archetype Reference for Antigravity**

```typescript
// Strict definition example for code synthesis
export const llm_risk_review = LlmAgent({
    name: "llm_risk_review",
    model: Gemini({
        model: MODEL_NAME,
        retry_options: types.HttpRetryOptions({ attempts: 3 }),
    }),
    instruction: "You are to analyze for the heart risk indicator and provide a localized, context-driven synthesis...",
    output_schema: RiskReviewResult,
    output_key: "risk_review",
});
```

### 5. Runtime Execution & Governance Layer (/governance/compliance.ts)
This module strictly isolates state processing runtimes, runtime memory management, and business logic validation to ensure bulletproof data handling:

- ADK Compute Runnets: All instances of the operational engine's Runner and context-sustaining MemoryRunner are managed exclusively here to protect state boundaries between async requests.
- Pre-Execution Guardrail: Inspects input data matrices before tool dispatching to reject impossible or anomalous values (e.g., clinical parameters outside sane human bounds).
- Mandatory Disclosure Appendage: A static, unalterable system string that must be embedded into every outgoing JSON packet, detailing that the analysis is an advanced statistical calculation based on machine learning weights and does not replace professional medical diagnosis.