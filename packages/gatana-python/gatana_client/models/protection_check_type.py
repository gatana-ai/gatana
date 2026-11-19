from enum import Enum


class ProtectionCheckType(str, Enum):
    INJECTION = "injection"
    PII = "pii"
    SECRETS = "secrets"

    def __str__(self) -> str:
        return str(self.value)
