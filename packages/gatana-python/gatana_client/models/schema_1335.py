from enum import Enum


class Schema1335(str, Enum):
    CLI = "cli"
    EXTERNAL = "external"
    NATIVE = "native"
    SLACK = "slack"
    UNKNOWN = "unknown"
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
