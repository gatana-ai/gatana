from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_899 import Schema899


T = TypeVar("T", bound="ListTeamServersResponse200")


@_attrs_define
class ListTeamServersResponse200:
    """
    Attributes:
        permissions (list[Schema899]): MCP server permissions granted to the team
    """

    permissions: list[Schema899]

    def to_dict(self) -> dict[str, Any]:
        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.to_dict()
            permissions.append(permissions_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "permissions": permissions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_899 import Schema899

        d = dict(src_dict)
        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = Schema899.from_dict(permissions_item_data)

            permissions.append(permissions_item)

        list_team_servers_response_200 = cls(
            permissions=permissions,
        )

        return list_team_servers_response_200
