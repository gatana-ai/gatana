from enum import Enum


class Schema471(str, Enum):
    MEMBER = "member"
    OWNER = "owner"

    def __str__(self) -> str:
        return str(self.value)
