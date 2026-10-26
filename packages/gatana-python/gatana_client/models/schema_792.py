from enum import Enum


class Schema792(str, Enum):
    DELETE = "delete"
    DISABLE = "disable"
    KEEP = "keep"

    def __str__(self) -> str:
        return str(self.value)
