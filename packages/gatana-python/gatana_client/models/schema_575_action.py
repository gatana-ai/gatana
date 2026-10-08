from enum import Enum


class Schema575Action(str, Enum):
    DENY = "deny"
    LOG = "log"
    MODIFY = "modify"

    def __str__(self) -> str:
        return str(self.value)
