from core.secret_manager_service import SecretManagerService

class VaultSecretManager:
    """
    Adapter/Wrapper for Vault/Secret operations, delegating to core SecretManagerService.
    """
    def __init__(self, project_id: str = None):
        self.service = SecretManagerService(project_id=project_id)

    def get_secret(self, secret_id: str, version_id: str = "latest") -> str:
        return self.service.fetch_secret(secret_id, version_id)
