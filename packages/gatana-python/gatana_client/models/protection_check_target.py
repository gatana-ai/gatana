from enum import Enum


class ProtectionCheckTarget(str, Enum):
    ARGUMENTS = "arguments"
    RESULT = "result"

    def __str__(self) -> str:
        return str(self.value)
