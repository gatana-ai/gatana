from enum import Enum


class Schema384(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    TENANT = "tenant"

    def __str__(self) -> str:
        return str(self.value)
