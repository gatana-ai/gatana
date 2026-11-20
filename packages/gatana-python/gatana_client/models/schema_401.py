from enum import Enum


class Schema401(str, Enum):
    JETBRAINS_MONO = "jetbrains-mono"
    SYSTEM_MONO = "system-mono"

    def __str__(self) -> str:
        return str(self.value)
