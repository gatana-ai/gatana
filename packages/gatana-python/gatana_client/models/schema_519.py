from enum import Enum


class Schema519(str, Enum):
    ANY = "any"
    SERVER_SCOPED = "server-scoped"
    SKIP = "skip"

    def __str__(self) -> str:
        return str(self.value)
