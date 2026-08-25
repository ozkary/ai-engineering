# Secured Agent Security Architecture Plan

This document outlines a security architecture plan for the `SecuredToolAgent`. It explains where ALLOW / WARN / DENY policies should reside, how to leverage `PreToolUse` hooks, how signature verification and MCP tools fit in, and how to introduce a sidecar for maximum protection.

---

## 1. Where should ALLOW / WARN / DENY live?

When an agent has Vault-resolved credentials, securing tool execution requires a defense-in-depth approach. Here is how policy enforcement should be distributed across the architectural layers:

| Layer | Responsibility | Verdict Support | Key Use Cases |
| :--- | :--- | :---: | :--- |
| **In-Process Policy / Harness Hooks** (e.g., `PreToolUse`) | Lightweight, context-aware validation of inputs & parameters within the ADK event loop. | **ALLOW / DENY** | - Checking if tool arguments contain sensitive tokens.<br>- Blocking file tools from writing to sensitive system paths (e.g., `.md`, `.sig` files). |
| **Sidecar Process** (Out-of-Process PDP) | High-trust policy decision point. Contains access control lists (ACLs) and mediates vault credential usage. | **ALLOW / WARN / DENY** | - Restricting tool access based on agent identity.<br>- Prompting for Human-in-the-Loop (HITL) authorization (**WARN**).<br>- Restricting rate/volume limits. |
| **Data-Plane Only** (Resource Level) | Ultimate fallback security enforcing IAM roles and DB permissions. | **ALLOW / DENY** | - GCP Service Account permissions (e.g., GCS bucket ACLs, BigQuery dataset roles). |

> [!IMPORTANT]
> **Rule of Thumb:** Use **Harness Hooks** for semantic verification of inputs/outputs (in-process). Use a **Sidecar** to guard high-trust credential resolution and identity-based access control (out-of-process). Use **Data-Plane** security as the final, immutable boundary.

---

## 2. Leveraging PreToolUse Hooks (`security/hooks.py`)

Currently, [hooks.py](adk/security/hooks.py) contains `guardrail_pre_tool_hook`, but it is not registered to the runner.

### How to improve the agent with PreToolUse:
1. **Register the Hook:** In [runner.py](adk/core/runner.py), register the hook to the agent or runner before invoking `runner.run_async`.
   ```python
   # Import the hook
   from security.hooks import guardrail_pre_tool_hook
   
   # Register it to the agent instance
   agent_instance.add_hook("pre_tool_use", guardrail_pre_tool_hook)
   ```
2. **Context-Aware Decisions:** `PreToolUseContext` provides `tool_name` and `args`. We can enforce policies dynamically:
   - If the tool is a system command or code executor, scan for shell injection patterns.
   - If the tool writes to files, enforce strict path sandboxing.

---

## 3. Integration with Signature Verification & MCP Tools

```mermaid
graph TD
    User([User Request]) --> Agent[SecuredToolAgent]
    
    subgraph Prompt Verification (Boot/Load Time)
        Agent --> load_prompt_asset
        load_prompt_asset --> Verifier[CryptographicPromptVerifier]
        Verifier -->|Verify HMAC| Secret[Vault/Secret Manager]
    end
    
    subgraph Tool Execution (Runtime)
        Agent -->|Calls Tool| Runner[ADK Runner]
        Runner -->|pre_tool_use| Hook[guardrail_pre_tool_hook]
        Hook -->|ALLOW| Exec[Execute Tool]
        Hook -->|DENY| Err[Block & Return Security Error]
        
        Exec -->|Local Tool| PyTool[Local Python Function]
        Exec -->|MCP Tool| MCP[MCP Server Tool]
    end
```

### Signature Verification
- **Role:** Guarantees **Static Integrity**. Ensures that instructions loaded from disk haven't been tampered with.
- **Hook Synergy:** Since signature files (`.signed.md` or `.sig`) and prompt files (`.md`) are stored on disk, the `PreToolUse` hook blocks file-writing tools from writing to or altering these files, preventing a compromised agent from rewriting its own prompt signature.

### MCP (Model Context Protocol) Tools
- **Role:** Run tools in external servers/processes.
- **Hook Synergy:** The ADK runner intercepts all tool executions, including MCP tools, prior to sending requests to the MCP server. Therefore, registering a `pre_tool_use` hook secures both local Python tools and external MCP tools universally.

---

## 4. Hardening Protection with a Sidecar

A sidecar architecture moves sensitive operations (like Vault credential storage and authorization policy execution) entirely out of the agent's runtime process.

```mermaid
sequenceDiagram
    participant Agent as Agent Process (Low Trust)
    participant Sidecar as Security Sidecar (High Trust)
    participant Vault as HashiCorp Vault
    participant Resource as Cloud Resource (GCS/BQ)

    Agent->>Sidecar: Request Tool Execution (e.g., read_gcs_bucket, args)
    Note over Sidecar: Validates caller identity<br/>& applies Policy Rules
    alt Policy = DENY
        Sidecar-->>Agent: Return Access Denied Error
    alt Policy = ALLOW
        Sidecar->>Vault: Fetch Short-Lived Credential
        Vault-->>Sidecar: Return Token/Key
        Sidecar->>Resource: Execute request with Credentials
        Resource-->>Sidecar: Return Data
        Sidecar-->>Agent: Return Cleaned Results
    end
```

### Why a Sidecar is More Secure:
1. **Memory Isolation:** The agent process never sees the Vault token or raw service account keys. Even if the agent is compromised via prompt injection or library vulnerability, the attacker cannot steal the credentials.
2. **Policy Tamper-Resistance:** The agent cannot override or uninstall hooks in a sidecar because the sidecar runs in a separate process space with its own security context.
3. **Audit Logging:** The sidecar provides a central, tamper-proof location to log all tool executions, parameters, and access decisions.
