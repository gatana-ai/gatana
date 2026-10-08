from enum import Enum


class CreateSecretStoreBodyType(str, Enum):
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"
    GCP_SECRET_MANAGER = "gcp_secret_manager"
    HASHICORP_VAULT = "hashicorp_vault"
    INFISICAL = "infisical"

    def __str__(self) -> str:
        return str(self.value)
