from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateUserProfileAssignmentRequest")


@_attrs_define
class CreateUserProfileAssignmentRequest:
    """
    Attributes:
        profile_id (str): ID of the profile to assign
        is_locked_by_org_owner (bool | Unset):
    """

    profile_id: str
    is_locked_by_org_owner: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        profile_id = self.profile_id

        is_locked_by_org_owner = self.is_locked_by_org_owner

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "profileId": profile_id,
            }
        )
        if is_locked_by_org_owner is not UNSET:
            field_dict["isLockedByOrgOwner"] = is_locked_by_org_owner

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        profile_id = d.pop("profileId")

        is_locked_by_org_owner = d.pop("isLockedByOrgOwner", UNSET)

        create_user_profile_assignment_request = cls(
            profile_id=profile_id,
            is_locked_by_org_owner=is_locked_by_org_owner,
        )

        create_user_profile_assignment_request.additional_properties = d
        return create_user_profile_assignment_request

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
