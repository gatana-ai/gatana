from enum import Enum


class Schema355(str, Enum):
    PLAYGROUND_CONVERSION = "playground-conversion"
    SIGNUP = "signup"

    def __str__(self) -> str:
        return str(self.value)
