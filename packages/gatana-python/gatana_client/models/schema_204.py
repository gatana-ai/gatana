from enum import Enum


class Schema204(str, Enum):
    VALUE_0 = "15m"
    VALUE_1 = "30m"
    VALUE_2 = "1h"
    VALUE_3 = "6h"
    VALUE_4 = "24h"
    VALUE_5 = "7d"
    VALUE_6 = "30d"

    def __str__(self) -> str:
        return str(self.value)
