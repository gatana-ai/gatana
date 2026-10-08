from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="TeamWithMemberCount")


@_attrs_define
class TeamWithMemberCount:
    """
    Attributes:
        id (str): Unique ID of the team
        tenant_id (str): ID of the tenant that owns the team
        name (str): Display name of the team, unique in the organization
        description (str): Human-readable description of the team
        is_scim_managed (bool): Whether the team is managed through SCIM provisioning
        scim_external_id (str): SCIM external ID of the team
        created_at (str): Time when the team was created
        updated_at (str): Time when the team was last updated
        member_count (float): Number of members in the team
        has_profile_attached (bool): Whether at least one profile is assigned to the team
    """

    id: str
    tenant_id: str
    name: str
    description: str
    is_scim_managed: bool
    scim_external_id: str
    created_at: str
    updated_at: str
    member_count: float
    has_profile_attached: bool

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        name = self.name

        description = self.description

        is_scim_managed = self.is_scim_managed

        scim_external_id = self.scim_external_id

        created_at = self.created_at

        updated_at = self.updated_at

        member_count = self.member_count

        has_profile_attached = self.has_profile_attached

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "name": name,
                "description": description,
                "isScimManaged": is_scim_managed,
                "scimExternalId": scim_external_id,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "memberCount": member_count,
                "hasProfileAttached": has_profile_attached,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        name = d.pop("name")

        description = d.pop("description")

        is_scim_managed = d.pop("isScimManaged")

        scim_external_id = d.pop("scimExternalId")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        member_count = d.pop("memberCount")

        has_profile_attached = d.pop("hasProfileAttached")

        team_with_member_count = cls(
            id=id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            is_scim_managed=is_scim_managed,
            scim_external_id=scim_external_id,
            created_at=created_at,
            updated_at=updated_at,
            member_count=member_count,
            has_profile_attached=has_profile_attached,
        )

        return team_with_member_count
