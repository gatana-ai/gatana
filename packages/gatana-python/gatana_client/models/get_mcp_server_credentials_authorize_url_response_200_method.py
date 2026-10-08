from enum import Enum


class GetMcpServerCredentialsAuthorizeUrlResponse200Method(str, Enum):
    APIKEY = "apikey"
    NONE = "none"
    OAUTH = "oauth"
    OAUTH_CLIENT_CREDENTIALS = "oauth-client-credentials"

    def __str__(self) -> str:
        return str(self.value)
