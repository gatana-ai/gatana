from enum import Enum


class Schema1219(str, Enum):
    ORGANIZATION = "organization"
    PRIVATE = "private"

    def __str__(self) -> str:
        return str(self.value)
