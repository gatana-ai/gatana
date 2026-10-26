from enum import Enum


class Schema356(str, Enum):
    JETBRAINS_MONO = "jetbrains-mono"
    SYSTEM_MONO = "system-mono"

    def __str__(self) -> str:
        return str(self.value)
