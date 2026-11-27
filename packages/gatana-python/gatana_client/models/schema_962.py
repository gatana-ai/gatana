from enum import Enum


class Schema962(str, Enum):
    DELETE = "delete"
    KEEP = "keep"

    def __str__(self) -> str:
        return str(self.value)
