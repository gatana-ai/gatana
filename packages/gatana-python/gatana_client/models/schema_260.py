from enum import Enum


class Schema260(str, Enum):
    GZIP = "gzip"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
