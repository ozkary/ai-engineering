# Gap Analysis


## Pending Work & Security Risks

### 1. Remaining Fallback Vulnerability (Pending Hardening)
To ensure the local environment continues to run test suites without network dependencies, `SecretManagerService` implements fallback options:
1. **Plain-Text Credentials Fallback:** Reads service account JSON key from `~/.gcp/ozkary-de-101.json`.
2. **HMAC Key Fallback:** Reads HMAC key from `~/.gcp/ozkary_agent_secret.key`.
3. **Hardcoded Fallback:** If both vault fetch and file reading fail, defaults to the hardcoded string `"dev-secret-key-do-not-use-in-production"`.

> [!CAUTION]
> **Pending Security Risks:**
> * **Local Privilege Escalation:** Service account credentials stored in plain-text under `~/.gcp/` can be read by compromised user processes.
> * **Hardcoded Verification Bypass:** If the agent fails to reach the Secret Manager, it falls back to the hardcoded key. An attacker could intentionally block network access to the API (or spoof a network timeout) to force the fallback, then recalculate signatures using the hardcoded key to bypass the verifier.

### 2. Next Steps (Pending Actions)
* [ ] **Conditional Fallback Disabling:** Implement an environment variable check (e.g. `ENV="production"`) inside `SecretManagerService`. If set to production, disable all plain-text and hardcoded fallbacks, enforcing a fail-closed policy.
* [ ] **Transition to KMS Asymmetric Keys:** For production environments, upgrade from symmetric HMAC verification to GCP KMS Asymmetric Signatures. This removes the need for the agent to have access to the signing key at all (only public keys are needed at runtime).

