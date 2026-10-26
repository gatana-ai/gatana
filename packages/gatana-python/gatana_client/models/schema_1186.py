from enum import Enum


class Schema1186(str, Enum):
    TEXTHTML = "text/html"
    TEXTMARKDOWN = "text/markdown"

    def __str__(self) -> str:
        return str(self.value)
