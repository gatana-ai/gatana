from enum import Enum


class Schema516(str, Enum):
    SPEC = "spec"
    SPECURL = "specUrl"

    def __str__(self) -> str:
        return str(self.value)
