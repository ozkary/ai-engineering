import os
from google.cloud import secretmanager

class SecretManagerService:
    """
    Service class handling interactions with GCP Secret Manager.
    """
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "ozkary-de-101")
        try:
            self.client = secretmanager.SecretManagerServiceClient()
        except Exception:
            self.client = None

    def fetch_secret(self, secret_id: str, version_id: str = "latest") -> str:
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        print(f"🔑 [SecretManagerService] Fetching from GCP Secret Manager...")
        if self.client:
            try:
                response = self.client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")
            except Exception as e:
                print(f"⚠️ [SecretManagerService] API fetch failed: {e}. Checking local fallback...")
        
        # Local fallback matching the user's service account json path configuration
        fallback_path = os.path.expanduser("~/.gcp/ozkary-de-101.json")
        if os.path.exists(fallback_path) and secret_id != "ozkary_agent_secret":
            print(f"📂 [SecretManagerService] Loading fallback credentials from local path: {fallback_path}")
            with open(fallback_path, "r", encoding="utf-8") as f:
                return f.read()

        # Handle local key fallback for ozkary_agent_secret
        if secret_id == "ozkary_agent_secret":
            key_fallback_path = os.path.expanduser("~/.gcp/ozkary_agent_secret.key")
            if os.path.exists(key_fallback_path):
                print(f"📂 [SecretManagerService] Loading hmac key from local path: {key_fallback_path}")
                with open(key_fallback_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            print("⚠️ [SecretManagerService] HMAC key secret not found, using default development key.")
            return "dev-secret-key-do-not-use-in-production"
                
        raise RuntimeError(f"Secret not found in GCP Secret Manager or local fallback.")

