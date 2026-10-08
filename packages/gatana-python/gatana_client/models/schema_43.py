from enum import Enum


class Schema43(str, Enum):
    HOSTED = "hosted"
    HTTPSTREAMING = "httpstreaming"
    OPENAPI = "openapi"
    SSE = "sse"
    STDIO = "stdio"

    def __str__(self) -> str:
        return str(self.value)
