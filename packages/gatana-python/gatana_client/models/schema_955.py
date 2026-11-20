from enum import Enum


class Schema955(str, Enum):
    AUDIT = "audit"
    OFF = "off"
    ON = "on"

    def __str__(self) -> str:
        return str(self.value)
