from enum import Enum


class Schema73(str, Enum):
    HTTPSTREAMING = "httpstreaming"
    SSE = "sse"
    STDIO = "stdio"

    def __str__(self) -> str:
        return str(self.value)
