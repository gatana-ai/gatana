from enum import Enum

class McpAuditLogVerbosity(str, Enum):
    DETAILED = "detailed"
    DETAILED_WITH_ERROR = "detailed-with-error"
    OFF = "off"
    TERSE = "terse"
    VERBOSE = "verbose"

    def __str__(self) -> str:
        return str(self.value)
