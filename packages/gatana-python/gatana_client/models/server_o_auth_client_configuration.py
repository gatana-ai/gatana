from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_531 import Schema531

T = TypeVar("T", bound="ServerOAuthClientConfiguration")


@_attrs_define
class ServerOAuthClientConfiguration:
    """
    Attributes:
        client_id (str):
        client_secret (str):
        grant_type (Schema531):
        client_auth_method (Literal['client_secret_basic'] | Literal['client_secret_post'] | Literal['none'] | str):
            Client authentication method used at the token endpoint
        scopes (str):
    """

    client_id: str
    client_secret: str
    grant_type: Schema531
    client_auth_method: Literal["client_secret_basic"] | Literal["client_secret_post"] | Literal["none"] | str
    scopes: str

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        client_secret = self.client_secret

        grant_type = self.grant_type.value

        client_auth_method: Literal["client_secret_basic"] | Literal["client_secret_post"] | Literal["none"] | str
        client_auth_method = self.client_auth_method

        scopes = self.scopes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "clientId": client_id,
                "clientSecret": client_secret,
                "grantType": grant_type,
                "clientAuthMethod": client_auth_method,
                "scopes": scopes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_id = d.pop("clientId")

        client_secret = d.pop("clientSecret")

        grant_type = Schema531(d.pop("grantType"))

        def _parse_client_auth_method(
            data: object,
        ) -> Literal["client_secret_basic"] | Literal["client_secret_post"] | Literal["none"] | str:
            componentsschemas_schema532_type_0 = cast(Literal["client_secret_basic"], data)
            if componentsschemas_schema532_type_0 != "client_secret_basic":
                raise ValueError(
                    f"/components/schemas/__schema532_type_0 must match const 'client_secret_basic', got '{componentsschemas_schema532_type_0}'"
                )
            return componentsschemas_schema532_type_0
            componentsschemas_schema532_type_1 = cast(Literal["client_secret_post"], data)
            if componentsschemas_schema532_type_1 != "client_secret_post":
                raise ValueError(
                    f"/components/schemas/__schema532_type_1 must match const 'client_secret_post', got '{componentsschemas_schema532_type_1}'"
                )
            return componentsschemas_schema532_type_1
            componentsschemas_schema532_type_2 = cast(Literal["none"], data)
            if componentsschemas_schema532_type_2 != "none":
                raise ValueError(
                    f"/components/schemas/__schema532_type_2 must match const 'none', got '{componentsschemas_schema532_type_2}'"
                )
            return componentsschemas_schema532_type_2
            return cast(Literal["client_secret_basic"] | Literal["client_secret_post"] | Literal["none"] | str, data)

        client_auth_method = _parse_client_auth_method(d.pop("clientAuthMethod"))

        scopes = d.pop("scopes")

        server_o_auth_client_configuration = cls(
            client_id=client_id,
            client_secret=client_secret,
            grant_type=grant_type,
            client_auth_method=client_auth_method,
            scopes=scopes,
        )

        return server_o_auth_client_configuration
