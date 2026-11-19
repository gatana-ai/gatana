from enum import Enum


class ProtectionOnAction(str, Enum):
    AUDIT = "audit"
    BLOCK = "block"
    OFF = "off"
    REDACT = "redact"

    def __str__(self) -> str:
        return str(self.value)
