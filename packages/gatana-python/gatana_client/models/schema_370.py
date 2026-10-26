from enum import Enum


class Schema370(str, Enum):
    ORGANIZATION = "organization"
    PRIVATE = "private"

    def __str__(self) -> str:
        return str(self.value)
