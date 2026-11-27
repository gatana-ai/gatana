from enum import Enum


class Schema1467(str, Enum):
    MAINTAIN = "maintain"
    READ = "read"

    def __str__(self) -> str:
        return str(self.value)
