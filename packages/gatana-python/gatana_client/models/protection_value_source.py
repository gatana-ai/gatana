from enum import Enum


class ProtectionValueSource(str, Enum):
    BUILTIN = "builtin"
    ORGANIZATION = "organization"
    SERVER = "server"

    def __str__(self) -> str:
        return str(self.value)
