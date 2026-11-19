from enum import Enum


class Schema665(str, Enum):
    ORGANIZE = "organize"
    READ = "read"
    SEND = "send"

    def __str__(self) -> str:
        return str(self.value)
