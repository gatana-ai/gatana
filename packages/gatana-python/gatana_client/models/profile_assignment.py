from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ProfileAssignment")


@_attrs_define
class ProfileAssignment:
    """
    Attributes:
        tenant_id (str): ID of the tenant that owns the assignment
        user_id (str): ID of the assigned user
        profile_id (str): ID of the assigned profile
        is_locked_by_org_owner (bool): Whether an organization owner locked the assignment; locked assignments take
            priority when the active profile is resolved
        created_at (str): Time when the assignment was created
        updated_at (str): Time when the assignment was last updated
    """

    tenant_id: str
    user_id: str
    profile_id: str
    is_locked_by_org_owner: bool
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        user_id = self.user_id

        profile_id = self.profile_id

        is_locked_by_org_owner = self.is_locked_by_org_owner

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tenantId": tenant_id,
                "userId": user_id,
                "profileId": profile_id,
                "isLockedByOrgOwner": is_locked_by_org_owner,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = d.pop("tenantId")

        user_id = d.pop("userId")

        profile_id = d.pop("profileId")

        is_locked_by_org_owner = d.pop("isLockedByOrgOwner")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        profile_assignment = cls(
            tenant_id=tenant_id,
            user_id=user_id,
            profile_id=profile_id,
            is_locked_by_org_owner=is_locked_by_org_owner,
            created_at=created_at,
            updated_at=updated_at,
        )

        return profile_assignment
