from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreatePersonalAccessTokenRequest")


@_attrs_define
class CreatePersonalAccessTokenRequest:
    """
    Attributes:
        name (str): Display name of the token
        profile_ids (list[str] | Unset):
    """

    name: str
    profile_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        profile_ids: list[str] | Unset = UNSET
        if not isinstance(self.profile_ids, Unset):
            profile_ids = self.profile_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if profile_ids is not UNSET:
            field_dict["profileIds"] = profile_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        profile_ids = cast(list[str], d.pop("profileIds", UNSET))

        create_personal_access_token_request = cls(
            name=name,
            profile_ids=profile_ids,
        )

        create_personal_access_token_request.additional_properties = d
        return create_personal_access_token_request

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
