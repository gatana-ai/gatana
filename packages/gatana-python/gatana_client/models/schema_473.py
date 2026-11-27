from enum import Enum


class Schema473(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UPGRADE = "upgrade"

    def __str__(self) -> str:
        return str(self.value)
