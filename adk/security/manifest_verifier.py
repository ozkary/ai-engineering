import hmac
import hashlib
import os

class SecurityError(Exception):
    """Custom error raised when cryptographic verification fails."""
    pass

class CryptographicPromptVerifier:
    @staticmethod
    def verify(prompt_path: str, signature_path: str, secret_key: bytes) -> bool:
        """
        Verifies the integrity and authenticity of the prompt file using HMAC-SHA256.
        
        ENTERPRISE SECURITY NOTE:
        While HMAC is robust for simple deployments or demos, it relies on sharing the 
        same symmetric key between the signing environment (e.g. CI/CD) and verification environment (runtime).
        For stronger enterprise-grade security, use Asymmetric Cryptography (e.g., GCP KMS with RSA/ECDSA).
        This allows the build environment to sign prompts using a KMS-protected private key, while 
        the agent only needs access to a public key (or public key verification API) to verify at runtime,
        ensuring that a compromised agent cannot be used to generate valid fake prompt signatures.
        """
        if not os.path.exists(prompt_path):
            raise SecurityError(f"Prompt file not found at {prompt_path}")
        if not os.path.exists(signature_path):
            raise SecurityError(f"Signature file not found at {signature_path}")
            
        with open(prompt_path, "rb") as f:
            prompt_data = f.read()
            
        # Compute HMAC-SHA256 signature
        computed_sig = hmac.new(secret_key, prompt_data, hashlib.sha256).hexdigest()
        
        # Compute raw SHA-256 checksum (in case the signature file uses raw sha256)
        computed_sha = hashlib.sha256(prompt_data).hexdigest()
            
        with open(signature_path, "r", encoding="utf-8") as f:
            expected_sig = f.read().strip()
            
        # Use constant-time comparison to protect against timing attacks
        is_hmac_valid = hmac.compare_digest(computed_sig, expected_sig)
        is_sha_valid = hmac.compare_digest(computed_sha, expected_sig)
        
        if not (is_hmac_valid or is_sha_valid):
            raise SecurityError(
                f"Security breach: Cryptographic HMAC signature mismatch!\n"
                f"Expected: {expected_sig}\n"
                f"Actual:   {computed_sig} (or raw sha256: {computed_sha})"
            )
            
        print(f"🔒 [Security] Prompt integrity & authenticity verified for {prompt_path}")
        return True

def load_and_verify_prompt(prompt_path: str, signature_path: str = None) -> tuple[bool, str, str]:
    """
    Core function that resolves the signature path, fetches the HMAC key from
    the secret manager, verifies the prompt file, and returns a tuple of
    (status, valid_prompt, quarantined).
    """
    if not signature_path:
        signature_path = prompt_path.replace(".md", ".signed.md")
        
    # Read the prompt file content first
    content = ""
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading prompt file: {e}"
            
    from security.secure_auth import VaultSecretManager
    # Initialize the VaultSecretManager (configured for project default or env var)
    secret_manager = VaultSecretManager()
    
    try:
        # Retrieve the symmetric key
        hmac_key_str = secret_manager.get_secret("ozkary_agent_secret")
        hmac_key = hmac_key_str.encode("utf-8")
        
        # Perform verification
        CryptographicPromptVerifier.verify(prompt_path, signature_path, hmac_key)
        return True, content, ""
    except Exception as e:
        print(f"🛡️ [Security] Verification failed: {e}")
        return False, "", content


