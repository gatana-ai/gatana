from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schema_181 import Schema181


T = TypeVar("T", bound="ServerCredentialsOauthTokens")


@_attrs_define
class ServerCredentialsOauthTokens:
    """
    Attributes:
        type_ (Literal['oauth']): Credential type discriminator, always "oauth"
        token_set (Schema181):
    """

    type_: Literal["oauth"]
    token_set: Schema181
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        token_set = self.token_set.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "tokenSet": token_set,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_181 import Schema181

        d = dict(src_dict)
        type_ = cast(Literal["oauth"], d.pop("type"))
        if type_ != "oauth":
            raise ValueError(f"type must match const 'oauth', got '{type_}'")

        token_set = Schema181.from_dict(d.pop("tokenSet"))

        server_credentials_oauth_tokens = cls(
            type_=type_,
            token_set=token_set,
        )

        server_credentials_oauth_tokens.additional_properties = d
        return server_credentials_oauth_tokens

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
