from enum import Enum


class Schema1057(str, Enum):
    FAILED = "Failed"
    PENDING = "Pending"
    READY = "Ready"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
