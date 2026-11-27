from enum import Enum


class Schema669(str, Enum):
    ORGANIZE = "organize"
    READ = "read"
    SEND = "send"

    def __str__(self) -> str:
        return str(self.value)
