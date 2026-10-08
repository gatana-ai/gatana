from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UpdateUserProfileAssignmentRequest")


@_attrs_define
class UpdateUserProfileAssignmentRequest:
    """
    Attributes:
        is_locked_by_org_owner (bool): Whether an organization owner locks the assignment
    """

    is_locked_by_org_owner: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_locked_by_org_owner = self.is_locked_by_org_owner

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isLockedByOrgOwner": is_locked_by_org_owner,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_locked_by_org_owner = d.pop("isLockedByOrgOwner")

        update_user_profile_assignment_request = cls(
            is_locked_by_org_owner=is_locked_by_org_owner,
        )

        update_user_profile_assignment_request.additional_properties = d
        return update_user_profile_assignment_request

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
