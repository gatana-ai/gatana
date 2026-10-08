from enum import Enum


class OAuthGrantType(str, Enum):
    AUTHORIZATION_CODE = "authorization_code"
    DEVICE_CODE = "device_code"

    def __str__(self) -> str:
        return str(self.value)
