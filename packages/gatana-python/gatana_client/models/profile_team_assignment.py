from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ProfileTeamAssignment")


@_attrs_define
class ProfileTeamAssignment:
    """
    Attributes:
        tenant_id (str): ID of the tenant that owns the assignment
        team_id (str): ID of the assigned team
        profile_id (str): ID of the assigned profile
        is_locked_by_org_owner (bool): Whether an organization owner locked the assignment; locked assignments take
            priority when the active profile is resolved
        created_at (str): Time when the assignment was created
        updated_at (str): Time when the assignment was last updated
    """

    tenant_id: str
    team_id: str
    profile_id: str
    is_locked_by_org_owner: bool
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        team_id = self.team_id

        profile_id = self.profile_id

        is_locked_by_org_owner = self.is_locked_by_org_owner

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tenantId": tenant_id,
                "teamId": team_id,
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

        team_id = d.pop("teamId")

        profile_id = d.pop("profileId")

        is_locked_by_org_owner = d.pop("isLockedByOrgOwner")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        profile_team_assignment = cls(
            tenant_id=tenant_id,
            team_id=team_id,
            profile_id=profile_id,
            is_locked_by_org_owner=is_locked_by_org_owner,
            created_at=created_at,
            updated_at=updated_at,
        )

        return profile_team_assignment
