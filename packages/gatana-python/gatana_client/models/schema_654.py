from enum import Enum


class Schema654(str, Enum):
    SPEC = "spec"
    SPECURL = "specUrl"

    def __str__(self) -> str:
        return str(self.value)
