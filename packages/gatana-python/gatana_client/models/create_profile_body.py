from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateProfileBody")


@_attrs_define
class CreateProfileBody:
    """
    Attributes:
        name (str): Display name of the profile
        description (str): Human-readable description of the profile
        is_open_to_all_users (bool): Whether all users in the tenant can use the profile without an explicit assignment
        is_restrictive (bool): Whether the profile restricts its users to only the servers in the profile; applies even
            to tenant owners
        is_code_mode_forced (bool | Unset): Whether MCP sessions that use the profile are forced into code mode
    """

    name: str
    description: str
    is_open_to_all_users: bool
    is_restrictive: bool
    is_code_mode_forced: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        is_open_to_all_users = self.is_open_to_all_users

        is_restrictive = self.is_restrictive

        is_code_mode_forced = self.is_code_mode_forced

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "isOpenToAllUsers": is_open_to_all_users,
                "isRestrictive": is_restrictive,
            }
        )
        if is_code_mode_forced is not UNSET:
            field_dict["isCodeModeForced"] = is_code_mode_forced

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        is_open_to_all_users = d.pop("isOpenToAllUsers")

        is_restrictive = d.pop("isRestrictive")

        is_code_mode_forced = d.pop("isCodeModeForced", UNSET)

        create_profile_body = cls(
            name=name,
            description=description,
            is_open_to_all_users=is_open_to_all_users,
            is_restrictive=is_restrictive,
            is_code_mode_forced=is_code_mode_forced,
        )

        create_profile_body.additional_properties = d
        return create_profile_body

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
