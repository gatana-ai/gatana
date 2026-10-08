from enum import Enum


class Schema481(str, Enum):
    HTTPSTREAMING = "httpstreaming"
    SSE = "sse"
    STDIO = "stdio"

    def __str__(self) -> str:
        return str(self.value)
