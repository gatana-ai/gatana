from enum import Enum


class Schema353(str, Enum):
    ADMIN = "admin"
    MAINTAINER = "maintainer"
    MEMBER = "member"

    def __str__(self) -> str:
        return str(self.value)
