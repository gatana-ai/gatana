from enum import Enum


class Schema673(str, Enum):
    STARTTLS = "starttls"
    TLS = "tls"

    def __str__(self) -> str:
        return str(self.value)
