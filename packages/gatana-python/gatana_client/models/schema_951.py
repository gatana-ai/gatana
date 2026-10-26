from enum import Enum


class Schema951(str, Enum):
    MAINTAINER = "maintainer"
    MEMBER = "member"

    def __str__(self) -> str:
        return str(self.value)
