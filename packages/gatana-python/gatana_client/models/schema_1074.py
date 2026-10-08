from enum import Enum


class Schema1074(str, Enum):
    CLI = "cli"
    EXTERNAL = "external"
    NATIVE = "native"
    UNKNOWN = "unknown"
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
