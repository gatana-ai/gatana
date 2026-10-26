from enum import Enum


class Schema715(str, Enum):
    APIKEY = "apikey"
    OAUTH = "oauth"

    def __str__(self) -> str:
        return str(self.value)
