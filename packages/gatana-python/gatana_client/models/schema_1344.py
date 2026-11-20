from enum import Enum


class Schema1344(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    TENANT = "tenant"

    def __str__(self) -> str:
        return str(self.value)
