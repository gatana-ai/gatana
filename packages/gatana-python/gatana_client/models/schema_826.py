from enum import Enum


class Schema826(str, Enum):
    COMPLETED = "completed"
    CRASHBACKOFF = "crashBackOff"
    FAILED = "failed"
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
