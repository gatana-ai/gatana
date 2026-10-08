from enum import Enum


class Schema967(str, Enum):
    ACTIVE = "active"
    DISABLED_AUTO = "disabled_auto"
    UNHEALTHY = "unhealthy"

    def __str__(self) -> str:
        return str(self.value)
