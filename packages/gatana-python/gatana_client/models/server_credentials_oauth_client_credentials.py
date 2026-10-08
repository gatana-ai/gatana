from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_192 import Schema192
    from ..models.server_o_auth_client_configuration_client_credentials import (
        ServerOAuthClientConfigurationClientCredentials,
    )


T = TypeVar("T", bound="ServerCredentialsOauthClientCredentials")


@_attrs_define
class ServerCredentialsOauthClientCredentials:
    """
    Attributes:
        type_ (Literal['oauth-client-credentials']): Credential type discriminator, always "oauth-client-credentials"
        client_config (ServerOAuthClientConfigurationClientCredentials | Unset):
        token_set (Schema192 | Unset):
    """

    type_: Literal["oauth-client-credentials"]
    client_config: ServerOAuthClientConfigurationClientCredentials | Unset = UNSET
    token_set: Schema192 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        client_config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.client_config, Unset):
            client_config = self.client_config.to_dict()

        token_set: dict[str, Any] | Unset = UNSET
        if not isinstance(self.token_set, Unset):
            token_set = self.token_set.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if client_config is not UNSET:
            field_dict["clientConfig"] = client_config
        if token_set is not UNSET:
            field_dict["tokenSet"] = token_set

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_192 import Schema192
        from ..models.server_o_auth_client_configuration_client_credentials import (
            ServerOAuthClientConfigurationClientCredentials,
        )

        d = dict(src_dict)
        type_ = cast(Literal["oauth-client-credentials"], d.pop("type"))
        if type_ != "oauth-client-credentials":
            raise ValueError(f"type must match const 'oauth-client-credentials', got '{type_}'")

        _client_config = d.pop("clientConfig", UNSET)
        client_config: ServerOAuthClientConfigurationClientCredentials | Unset
        if isinstance(_client_config, Unset):
            client_config = UNSET
        else:
            client_config = ServerOAuthClientConfigurationClientCredentials.from_dict(_client_config)

        _token_set = d.pop("tokenSet", UNSET)
        token_set: Schema192 | Unset
        if isinstance(_token_set, Unset):
            token_set = UNSET
        else:
            token_set = Schema192.from_dict(_token_set)

        server_credentials_oauth_client_credentials = cls(
            type_=type_,
            client_config=client_config,
            token_set=token_set,
        )

        server_credentials_oauth_client_credentials.additional_properties = d
        return server_credentials_oauth_client_credentials

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
