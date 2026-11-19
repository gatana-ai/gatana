from enum import Enum


class Schema438Encoding(str, Enum):
    BASE64 = "base64"
    UTF8 = "utf8"

    def __str__(self) -> str:
        return str(self.value)
