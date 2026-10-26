from enum import Enum


class Schema344(str, Enum):
    FRAUNCES = "fraunces"
    INTER = "inter"
    SYSTEM_SANS = "system-sans"
    SYSTEM_SERIF = "system-serif"

    def __str__(self) -> str:
        return str(self.value)
