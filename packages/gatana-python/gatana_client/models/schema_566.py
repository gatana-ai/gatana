from enum import Enum


class Schema566(str, Enum):
    SPEC = "spec"
    SPECURL = "specUrl"

    def __str__(self) -> str:
        return str(self.value)
