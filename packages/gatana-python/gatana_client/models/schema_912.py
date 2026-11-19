from enum import Enum


class Schema912(str, Enum):
    ENGLISH = "english"
    MULTILINGUAL = "multilingual"

    def __str__(self) -> str:
        return str(self.value)
