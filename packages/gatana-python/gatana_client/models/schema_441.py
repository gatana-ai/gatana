from enum import Enum


class Schema441(str, Enum):
    SERVERS = "servers"
    TEAMS = "teams"
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
