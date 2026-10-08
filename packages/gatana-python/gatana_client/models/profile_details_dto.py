from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1010 import Schema1010


T = TypeVar("T", bound="ProfileDetailsDto")


@_attrs_define
class ProfileDetailsDto:
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
        servers (list[Schema1010]): Servers included in the profile
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
    servers: list[Schema1010]

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

        servers = []
        for componentsschemas_schema1009_item_data in self.servers:
            componentsschemas_schema1009_item = componentsschemas_schema1009_item_data.to_dict()
            servers.append(componentsschemas_schema1009_item)

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
                "servers": servers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1010 import Schema1010

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

        servers = []
        _servers = d.pop("servers")
        for componentsschemas_schema1009_item_data in _servers:
            componentsschemas_schema1009_item = Schema1010.from_dict(componentsschemas_schema1009_item_data)

            servers.append(componentsschemas_schema1009_item)

        profile_details_dto = cls(
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
            servers=servers,
        )

        return profile_details_dto
