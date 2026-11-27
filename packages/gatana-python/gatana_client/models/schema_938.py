from enum import Enum


class Schema938(str, Enum):
    ENGLISH = "english"
    MULTILINGUAL = "multilingual"

    def __str__(self) -> str:
        return str(self.value)
