from enum import Enum


class Schema294(str, Enum):
    GATANA = "gatana"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
