from enum import Enum


class Schema709(str, Enum):
    ENGLISH = "english"
    MULTILINGUAL = "multilingual"

    def __str__(self) -> str:
        return str(self.value)
