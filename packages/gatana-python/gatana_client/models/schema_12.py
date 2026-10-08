from enum import Enum


class Schema12(str, Enum):
    ALL = "all"
    SERVICE_ACCOUNT = "service-account"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
