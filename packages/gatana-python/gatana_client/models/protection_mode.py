from enum import Enum


class ProtectionMode(str, Enum):
    AUDIT = "audit"
    OFF = "off"
    ON = "on"

    def __str__(self) -> str:
        return str(self.value)
