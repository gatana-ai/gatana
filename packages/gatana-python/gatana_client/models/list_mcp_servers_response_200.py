from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.list_mcp_servers_response_200_servers_item import ListMcpServersResponse200ServersItem


T = TypeVar("T", bound="ListMcpServersResponse200")


@_attrs_define
class ListMcpServersResponse200:
    """
    Attributes:
        servers (list[ListMcpServersResponse200ServersItem]):
    """

    servers: list[ListMcpServersResponse200ServersItem]

    def to_dict(self) -> dict[str, Any]:
        servers = []
        for servers_item_data in self.servers:
            servers_item = servers_item_data.to_dict()
            servers.append(servers_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "servers": servers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_mcp_servers_response_200_servers_item import ListMcpServersResponse200ServersItem

        d = dict(src_dict)
        servers = []
        _servers = d.pop("servers")
        for servers_item_data in _servers:
            servers_item = ListMcpServersResponse200ServersItem.from_dict(servers_item_data)

            servers.append(servers_item)

        list_mcp_servers_response_200 = cls(
            servers=servers,
        )

        return list_mcp_servers_response_200
