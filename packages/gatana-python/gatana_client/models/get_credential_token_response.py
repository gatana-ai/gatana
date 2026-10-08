from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_657 import Schema657
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetCredentialTokenResponse")


@_attrs_define
class GetCredentialTokenResponse:
    """
    Attributes:
        type_ (Schema657):
        access_token (str | Unset):
        expires_at (float | Unset):
        apikeys (list[list[str]] | Unset):
    """

    type_: Schema657
    access_token: str | Unset = UNSET
    expires_at: float | Unset = UNSET
    apikeys: list[list[str]] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        access_token = self.access_token

        expires_at = self.expires_at

        apikeys: list[list[str]] | Unset = UNSET
        if not isinstance(self.apikeys, Unset):
            apikeys = []
            for componentsschemas_schema662_item_data in self.apikeys:
                componentsschemas_schema662_item = []
                for componentsschemas_schema662_item_item_data in componentsschemas_schema662_item_data:
                    componentsschemas_schema662_item_item: str
                    componentsschemas_schema662_item_item = componentsschemas_schema662_item_item_data
                    componentsschemas_schema662_item.append(componentsschemas_schema662_item_item)

                apikeys.append(componentsschemas_schema662_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
            }
        )
        if access_token is not UNSET:
            field_dict["accessToken"] = access_token
        if expires_at is not UNSET:
            field_dict["expiresAt"] = expires_at
        if apikeys is not UNSET:
            field_dict["apikeys"] = apikeys

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = Schema657(d.pop("type"))

        access_token = d.pop("accessToken", UNSET)

        expires_at = d.pop("expiresAt", UNSET)

        _apikeys = d.pop("apikeys", UNSET)
        apikeys: list[list[str]] | Unset = UNSET
        if _apikeys is not UNSET:
            apikeys = []
            for componentsschemas_schema662_item_data in _apikeys:
                componentsschemas_schema662_item = []
                _componentsschemas_schema662_item = componentsschemas_schema662_item_data
                for componentsschemas_schema662_item_item_data in _componentsschemas_schema662_item:

                    def _parse_componentsschemas_schema662_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema662_item_item = _parse_componentsschemas_schema662_item_item(
                        componentsschemas_schema662_item_item_data
                    )

                    componentsschemas_schema662_item.append(componentsschemas_schema662_item_item)

                apikeys.append(componentsschemas_schema662_item)

        get_credential_token_response = cls(
            type_=type_,
            access_token=access_token,
            expires_at=expires_at,
            apikeys=apikeys,
        )

        return get_credential_token_response
