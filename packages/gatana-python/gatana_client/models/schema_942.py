from enum import Enum


class Schema942(str, Enum):
    MAINTAINER = "maintainer"
    MEMBER = "member"

    def __str__(self) -> str:
        return str(self.value)
