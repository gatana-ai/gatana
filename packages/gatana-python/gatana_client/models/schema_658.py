from enum import Enum


class Schema658(str, Enum):
    SPEC = "spec"
    SPECURL = "specUrl"

    def __str__(self) -> str:
        return str(self.value)
