import os
from google.auth.transport.requests import Request
from google.oauth2 import service_account


class CloudAuthContext:
    """
    Singleton Cloud Authentication Context Manager.
    Handles credential parsing, token refresh lifecycles, and HTTP headers.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CloudAuthContext, cls).__new__(cls)
            cls._initialized = False
        return cls._instance

    def __init__(self):
        # Prevent re-initialization if the singleton is already hydrated
        if self._initialized:
            return

        print("[Auth] Initializing Singleton Cloud Account Context...")
        self.sa_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")

        if not self.sa_key or not os.path.exists(self.sa_key):
            raise FileNotFoundError(
                f"Missing or invalid GOOGLE_APPLICATION_CREDENTIALS file path: '{self.sa_key}'"
            )

        # Set the unified scope for tool identities
        self.scopes = ["https://www.googleapis.com/auth/cloud-platform"]

        # Hydrate base credentials from your managed key file
        self.creds = service_account.Credentials.from_service_account_file(
            self.sa_key, scopes=self.scopes
        )

        self.refresh_token()
        self._initialized = True

    def refresh_token(self):
        """Forces a transport request refresh to guarantee token validity."""
        print("📡 [Auth] Requesting fresh OAuth2 Token lifecycle lock...")
        request = Request()
        self.creds.refresh(request)
        print(f"✅ [Auth] Context Token Secured. Expires: {self.creds.expiry}")

    @property
    def credentials(self) -> service_account.Credentials:
        """Returns the active cached Google credentials object."""
        # Check if the token is close to expiring, refresh if necessary
        if self.creds.expired:
            self.refresh_token()
        return self.creds

    @property
    def http_headers(self) -> dict:
        """
        Generates fresh, authenticated request headers for raw REST/gRPC
        operations within custom MCP tools.
        """
        # Safety check for token expiration before generating header values
        if self.creds.expired:
            self.refresh_token()

        return {
            "Authorization": f"Bearer {self.creds.token}",
            "x-goog-user-project": self.project_id,
            "Content-Type": "application/json",
        }
