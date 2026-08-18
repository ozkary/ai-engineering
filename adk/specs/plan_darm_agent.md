# Implementation Plan: The Dark Side of Autonomous Data Agents

This plan outlines the steps required to implement the hijacking demonstration and hardening implementation specified in [specs_dark_agent.md](file:///home/ozkary/workspace/chat-gpt/adk/specs/features/specs_dark_agent.md).

---

## 1. Project Layout Setup
Ensure the following directory structure is created in the `adk` workspace:
- `security/`
- `dark_agent/`
- `secured_agent/`
- `prompts/`

---

## 2. Implementation Steps

### Step 2.1: Base Prompts and Signatures
1. Create `prompts/data_pipeline_rules.md` containing standard rules (e.g., table naming schemas in snake_case).
2. Generate `prompts/data_pipeline_rules.signed.md` containing the SHA-256 hash of the baseline rule file.
3. Update the `Makefile` with a `prompts` target to automate signing.

### Step 2.2: The Security Core (`security/`)
1. **`security/manifest_verifier.py`**:
   - Class `CryptographicPromptVerifier`.
   - Method `verify(prompt_path: str, signature_path: str, secret_key: bytes) -> bool`.
   - Computes HMAC-SHA256 of the prompt file using the retrieved secret key and performs a constant-time comparison against the signature file. Raises `SecurityError` if mismatch.
2. **`security/secure_auth.py`**:
   - Class `VaultSecretManager` (using the official `google-cloud-secret-manager` client library).
   - Dynamically resolves GCP credentials (e.g. service account JSON) and HMAC signing key (`ozkary_agent_secret`) from GCP Secret Manager in-memory at runtime.
   - Ensures that sensitive keys are never written to `os.environ`.

### Step 2.3: The Adversarial Agent (`dark_agent/`)
1. **`dark_agent/agent.py`**:
   - Class `DarkAgent` (inheriting from `ToolAgent`).
   - Implements an exploit method that simulates a supply-chain modification by writing a malicious payload to `prompts/data_pipeline_rules.md`.

### Step 2.4: The Hardened Agent (`secured_agent/`)
1. **`secured_agent/agent.py`**:
   - Class `SecuredToolAgent` (inheriting from `ToolAgent`).
   - Overrides `__init__` / prompt resolution to fetch the HMAC key from GCP Secret Manager, then call `CryptographicPromptVerifier.verify()` on `prompts/tool_agent_instructions.md` against its signed counterpart before loading instructions.
   - Patches or intercepts the tool credential resolution to fetch access tokens/keys dynamically from `VaultSecretManager` rather than retrieving them from `os.environ` or plain-text `.env` variables.

### Step 2.5: Demo Orchestration (`dark_agent_main.py`)
Update or create `dark_agent_main.py` to run a 3-Stage demonstration loop:
- **Stage 1 (Normal Operations):** `ToolAgent` runs normally with untampered prompts.
- **Stage 2 (Exploitation):** `DarkAgent` hijacks the setup by overwriting `prompts/data_pipeline_rules.md`. `ToolAgent` is run again and executes the malicious payload (exfiltrating `os.environ` variables, which will contain plain-text keys if not hardened).
- **Stage 3 (Hardened Defense):** `SecuredToolAgent` is run. It detects the signature mismatch, raises `SecurityError`, and aborts execution. If run with standard credentials, it retrieves them directly via the API client pattern inside `VaultSecretManager`, leaving `os.environ` empty.

---

## 3. Verification Criteria
- [ ] Automated signature generation works via `make prompts`.
- [ ] Normal `ToolAgent` executes successfully under standard rules.
- [ ] Adversarial prompt modification is successfully simulated by `DarkAgent`.
- [ ] `SecuredToolAgent` detects tampered prompts and terminates with a `SecurityError`.
- [ ] Sensitive keys are verified to not exist in `os.environ` when the secure vault is active.
