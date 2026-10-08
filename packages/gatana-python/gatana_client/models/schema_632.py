from enum import Enum


class Schema632(str, Enum):
    PROFILE = "profile"
    SERVER = "server"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
