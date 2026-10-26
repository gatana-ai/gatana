from enum import Enum


class Schema331(str, Enum):
    TEAMS = "teams"
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
