from enum import Enum


class Schema403(str, Enum):
    MEMBER = "member"
    OWNER = "owner"

    def __str__(self) -> str:
        return str(self.value)
