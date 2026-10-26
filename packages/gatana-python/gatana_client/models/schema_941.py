from enum import Enum


class Schema941(str, Enum):
    MAINTAINER = "maintainer"
    MEMBER = "member"

    def __str__(self) -> str:
        return str(self.value)
