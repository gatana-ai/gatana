from enum import Enum


class Schema885(str, Enum):
    DELETE = "delete"
    DISABLE = "disable"
    KEEP = "keep"

    def __str__(self) -> str:
        return str(self.value)
