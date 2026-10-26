from enum import Enum


class Schema767(str, Enum):
    ENGLISH = "english"
    MULTILINGUAL = "multilingual"

    def __str__(self) -> str:
        return str(self.value)
