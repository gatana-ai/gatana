from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ProfileListItemDto")


@_attrs_define
class ProfileListItemDto:
    """
    Attributes:
        tenant_id (str): ID of the tenant that owns the profile
        id (str): Unique ID of the profile
        created_by (str): ID of the user who created the profile
        name (str): Display name of the profile
        description (str): Human-readable description of the profile
        is_open_to_all_users (bool): Whether all users in the tenant can use the profile without an explicit assignment
        is_restrictive (bool): Whether the profile restricts its users to only the servers in the profile; applies even
            to tenant owners
        is_code_mode_forced (bool): Whether MCP sessions that use the profile are forced into code mode
        created_at (str): Time when the profile was created
        updated_at (str): Time when the profile was last updated
        num_servers (float): Number of servers included in the profile
        num_assigned_users (float): Number of distinct users assigned to the profile, directly or through a team
        num_assigned_teams (float): Number of teams assigned to the profile
        num_mappings (float): Number of claim mappings that assign the profile
        num_users_pats (float): Number of distinct users that reference the profile from a personal access token
    """

    tenant_id: str
    id: str
    created_by: str
    name: str
    description: str
    is_open_to_all_users: bool
    is_restrictive: bool
    is_code_mode_forced: bool
    created_at: str
    updated_at: str
    num_servers: float
    num_assigned_users: float
    num_assigned_teams: float
    num_mappings: float
    num_users_pats: float

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        id = self.id

        created_by = self.created_by

        name = self.name

        description = self.description

        is_open_to_all_users = self.is_open_to_all_users

        is_restrictive = self.is_restrictive

        is_code_mode_forced = self.is_code_mode_forced

        created_at = self.created_at

        updated_at = self.updated_at

        num_servers = self.num_servers

        num_assigned_users = self.num_assigned_users

        num_assigned_teams = self.num_assigned_teams

        num_mappings = self.num_mappings

        num_users_pats = self.num_users_pats

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tenantId": tenant_id,
                "id": id,
                "createdBy": created_by,
                "name": name,
                "description": description,
                "isOpenToAllUsers": is_open_to_all_users,
                "isRestrictive": is_restrictive,
                "isCodeModeForced": is_code_mode_forced,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "numServers": num_servers,
                "numAssignedUsers": num_assigned_users,
                "numAssignedTeams": num_assigned_teams,
                "numMappings": num_mappings,
                "numUsersPats": num_users_pats,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = d.pop("tenantId")

        id = d.pop("id")

        created_by = d.pop("createdBy")

        name = d.pop("name")

        description = d.pop("description")

        is_open_to_all_users = d.pop("isOpenToAllUsers")

        is_restrictive = d.pop("isRestrictive")

        is_code_mode_forced = d.pop("isCodeModeForced")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        num_servers = d.pop("numServers")

        num_assigned_users = d.pop("numAssignedUsers")

        num_assigned_teams = d.pop("numAssignedTeams")

        num_mappings = d.pop("numMappings")

        num_users_pats = d.pop("numUsersPats")

        profile_list_item_dto = cls(
            tenant_id=tenant_id,
            id=id,
            created_by=created_by,
            name=name,
            description=description,
            is_open_to_all_users=is_open_to_all_users,
            is_restrictive=is_restrictive,
            is_code_mode_forced=is_code_mode_forced,
            created_at=created_at,
            updated_at=updated_at,
            num_servers=num_servers,
            num_assigned_users=num_assigned_users,
            num_assigned_teams=num_assigned_teams,
            num_mappings=num_mappings,
            num_users_pats=num_users_pats,
        )

        return profile_list_item_dto
