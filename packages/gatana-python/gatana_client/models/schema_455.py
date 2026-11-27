from enum import Enum


class Schema455(str, Enum):
    TEAMS = "teams"
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
