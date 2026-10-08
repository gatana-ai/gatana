from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.profile_server_tools import ProfileServerTools


T = TypeVar("T", bound="ProfileServerToolsResponse")


@_attrs_define
class ProfileServerToolsResponse:
    """
    Attributes:
        servers (list[ProfileServerTools]): Tool configuration of the profile, one entry per server of the profile
    """

    servers: list[ProfileServerTools]

    def to_dict(self) -> dict[str, Any]:
        servers = []
        for componentsschemas_schema1027_item_data in self.servers:
            componentsschemas_schema1027_item = componentsschemas_schema1027_item_data.to_dict()
            servers.append(componentsschemas_schema1027_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "servers": servers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_server_tools import ProfileServerTools

        d = dict(src_dict)
        servers = []
        _servers = d.pop("servers")
        for componentsschemas_schema1027_item_data in _servers:
            componentsschemas_schema1027_item = ProfileServerTools.from_dict(componentsschemas_schema1027_item_data)

            servers.append(componentsschemas_schema1027_item)

        profile_server_tools_response = cls(
            servers=servers,
        )

        return profile_server_tools_response
