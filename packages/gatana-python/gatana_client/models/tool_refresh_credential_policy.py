from enum import Enum


class ToolRefreshCredentialPolicy(str, Enum):
    ANY = "any"
    SERVER_SCOPED = "server-scoped"
    SKIP = "skip"

    def __str__(self) -> str:
        return str(self.value)
