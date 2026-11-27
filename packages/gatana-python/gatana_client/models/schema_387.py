from enum import Enum


class Schema387(str, Enum):
    TEAMS = "teams"
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
