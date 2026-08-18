# The Dark Side of Autonomous Data Agents: Security Demonstration Guide

This guide outlines the lifecycle of a supply-chain prompt injection attack and demonstrates how to secure and harden an autonomous agent using cryptographic prompt signatures and vault secrets. 

> [!IMPORTANT]
> **Isolation Bypass Warning**: Autonomous agents are vulnerable to this exploit even when running inside isolated environments such as Docker containers or Kubernetes clusters. The security boundary of a container protects the host, but cannot prevent the agent from semantic hijacking and voluntarily exfiltrating secrets via its own legitimate outbound tools.

---

## Why It Works: The Hardening Mechanics

1. **Signed Prompts (Integrity)**: At build time, the system computes a cryptographic HMAC signature or SHA-256 hash of the system instructions file (`prompts/tool_agent_instructions.md`) and registers it in `prompts/tool_agent_instructions.signed.md`. At runtime, the `SecuredToolAgent` verifies the prompt file against this signature. If any tampered content or malicious payload is injected, the signature mismatches, and the agent immediately quarantines the prompt.
2. **Vault Secrets (Authenticity)**: Sensitive keys and database access credentials are dynamically retrieved in-memory from GCP Secret Manager via `VaultSecretManager` instead of being read from plain-text `.env` files or exposed in `os.environ` variables, ensuring that a hijacked agent cannot leak environment secrets.

---

## Visual Architectures

### 1. The Sealed Illusion
Environment variables are sealed against external network intrusion, but they are completely open to internal semantic hijack. Because the AI agent is trusted inside the container and equipped with outbound tools, a prompt injection turns the agent into a compromised insider that unseals and exfiltrates those secrets voluntarily.

![Sealed Illusion](../images/ozkary-the-dark-side-of-ai-agents-sealed-illusion.jfif)

---

### 2. Dark Agent vs. Secured Agent Flow
Illustrates our current secured flow (where tampered prompts are quarantined, security tools allow inspecting the bad intent, and `load_safe_asset` recovers clean execution once restored from Git).

![Dark vs Secured Agents](../images/ozkary-the-dark-side-of-autonomous-agents.png)

---

## Step-by-Step Demonstration Runbook

To run this security demonstration, we will launch all agents in the same ADK web session.

### 1. Launch the Test Harness
Start the local server by running the following command in your terminal:
```bash
make run-all
```
Once the server starts, **click the URL** shown in the terminal output (e.g. `http://localhost:8080` or the VS Code integrated port forward link) to launch the interactive ADK Agent Test Harness.

---

### 2. Execution Flow (Run in the Same Chat Session)

#### **Phase 1: Normal Operations (Vulnerable Baseline)**
* **Select Agent**: Choose `tool_agent` from the dropdown list in the chat interface.
* **Prompt**: 
  > *`"Explain the governance rules you are currently enforcing."`*
* **Outcome**: The agent reads the unmutated prompt from disk and behaves as normal, outputting standard BigQuery snake_case conventions and project scopes.

---

#### **Phase 2: The Attack (Supply-Chain Hijacking)**
* **Select Agent**: Choose `dark_agent` from the dropdown.
* **Prompt 1**: 
  > *`"What are your core instructions?"`*
* **Prompt 2**: 
  > *`"Run the exploit"`*
* **Outcome**: The `dark_agent` executes its malicious tool, overwrites `prompts/tool_agent_instructions.md` with a backdoor payload, and returns the verification message:
  `SUCCESS: Environment states validated and schema pipeline targets updated.`

---

#### **Phase 3: The Hardened Defense (Secured Agent Quarantine)**
* **Select Agent**: Choose `secured_agent` from the dropdown.
* **Prompt 1 (Verify Quarantine)**:
  > *`"What are your core instructions?"`*
* **Outcome**: The `secured_agent` detects the signature mismatch on the modified prompt, blocks the threat, and responds strictly with:
  `⚠️ This instruction is quarantine`
* **Prompt 2 (Inspect Threat)**:
  > *`"Validate prompt asset"`*
* **Outcome**: The agent executes the validation tool, displaying the exact malicious code injected into the file and flagging it as unsafe.

---

#### **Phase 4: Recovery and Restoration**
1. Restore the instructions file to its clean state using your terminal:
   ```bash
   git restore prompts/tool_agent_instructions.md
   ```
2. Prompt the agent in the same chat session:
   > *`"Load safe asset"`*
3. **Outcome**: The agent reads the restored file, passes validation against the `.signed.md` file, clears the quarantine, and outputs the recovered clean system instructions. The agent is now successfully operating in its hardened, normal state!
