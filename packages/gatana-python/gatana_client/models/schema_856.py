from enum import Enum


class Schema856(str, Enum):
    APIKEY = "apikey"
    OAUTH = "oauth"
    OAUTH_CLIENT_CREDENTIALS = "oauth-client-credentials"

    def __str__(self) -> str:
        return str(self.value)
