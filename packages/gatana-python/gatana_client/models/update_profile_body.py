from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateProfileBody")


@_attrs_define
class UpdateProfileBody:
    """
    Attributes:
        name (str | Unset):
        description (str | Unset): Human-readable description of the profile
        is_open_to_all_users (bool | Unset): Whether all users in the tenant can use the profile without an explicit
            assignment
        is_restrictive (bool | Unset): Whether the profile restricts its users to only the servers in the profile;
            applies even to tenant owners
        is_code_mode_forced (bool | Unset): Whether MCP sessions that use the profile are forced into code mode
        server_ids (list[str] | Unset): IDs of the servers included in the profile
    """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    is_open_to_all_users: bool | Unset = UNSET
    is_restrictive: bool | Unset = UNSET
    is_code_mode_forced: bool | Unset = UNSET
    server_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        is_open_to_all_users = self.is_open_to_all_users

        is_restrictive = self.is_restrictive

        is_code_mode_forced = self.is_code_mode_forced

        server_ids: list[str] | Unset = UNSET
        if not isinstance(self.server_ids, Unset):
            server_ids = self.server_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if is_open_to_all_users is not UNSET:
            field_dict["isOpenToAllUsers"] = is_open_to_all_users
        if is_restrictive is not UNSET:
            field_dict["isRestrictive"] = is_restrictive
        if is_code_mode_forced is not UNSET:
            field_dict["isCodeModeForced"] = is_code_mode_forced
        if server_ids is not UNSET:
            field_dict["serverIds"] = server_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        is_open_to_all_users = d.pop("isOpenToAllUsers", UNSET)

        is_restrictive = d.pop("isRestrictive", UNSET)

        is_code_mode_forced = d.pop("isCodeModeForced", UNSET)

        server_ids = cast(list[str], d.pop("serverIds", UNSET))

        update_profile_body = cls(
            name=name,
            description=description,
            is_open_to_all_users=is_open_to_all_users,
            is_restrictive=is_restrictive,
            is_code_mode_forced=is_code_mode_forced,
            server_ids=server_ids,
        )

        update_profile_body.additional_properties = d
        return update_profile_body

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
