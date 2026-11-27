from enum import Enum


class Schema647(str, Enum):
    NODE24 = "node24"
    PYTHON313 = "python313"

    def __str__(self) -> str:
        return str(self.value)
