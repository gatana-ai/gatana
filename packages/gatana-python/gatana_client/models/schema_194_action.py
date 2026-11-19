from enum import Enum


class Schema194Action(str, Enum):
    ALLOW = "allow"
    AUDIT = "audit"
    BLOCK = "block"
    DENY = "deny"
    REDACT = "redact"

    def __str__(self) -> str:
        return str(self.value)
