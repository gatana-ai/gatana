from enum import Enum


class Schema1033(str, Enum):
    GZIP = "gzip"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
