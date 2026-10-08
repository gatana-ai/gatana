from enum import Enum


class Schema392(str, Enum):
    CLIENT = "client"
    TOKEN = "token"

    def __str__(self) -> str:
        return str(self.value)
