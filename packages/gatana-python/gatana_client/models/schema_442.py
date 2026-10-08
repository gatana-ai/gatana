from enum import Enum


class Schema442(str, Enum):
    EXTERNAL_OIDC = "external-oidc"
    EXTERNAL_SAML = "external-saml"
    NATIVE = "native"

    def __str__(self) -> str:
        return str(self.value)
