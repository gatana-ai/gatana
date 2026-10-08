from enum import Enum


class GetMcpServerCredentialsAuthorizeUrlReturnTo(str, Enum):
    DETAILS = "details"
    PROFILE = "profile"
    PROFILE_SERVER = "profile-server"
    SETTINGS = "settings"
    THANK_YOU_PAGE = "thank-you-page"

    def __str__(self) -> str:
        return str(self.value)
