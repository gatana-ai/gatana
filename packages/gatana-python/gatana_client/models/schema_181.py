from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema181")


@_attrs_define
class Schema181:
    """
    Attributes:
        access_token (str): OAuth access token
        access_token_expires_at (float | Unset):
        id_token (str | Unset):
        refresh_token (str | Unset):
    """

    access_token: str
    access_token_expires_at: float | Unset = UNSET
    id_token: str | Unset = UNSET
    refresh_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        access_token_expires_at = self.access_token_expires_at

        id_token = self.id_token

        refresh_token = self.refresh_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accessToken": access_token,
            }
        )
        if access_token_expires_at is not UNSET:
            field_dict["accessTokenExpiresAt"] = access_token_expires_at
        if id_token is not UNSET:
            field_dict["idToken"] = id_token
        if refresh_token is not UNSET:
            field_dict["refreshToken"] = refresh_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_token = d.pop("accessToken")

        access_token_expires_at = d.pop("accessTokenExpiresAt", UNSET)

        id_token = d.pop("idToken", UNSET)

        refresh_token = d.pop("refreshToken", UNSET)

        schema_181 = cls(
            access_token=access_token,
            access_token_expires_at=access_token_expires_at,
            id_token=id_token,
            refresh_token=refresh_token,
        )

        schema_181.additional_properties = d
        return schema_181

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
