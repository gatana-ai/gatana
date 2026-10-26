from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.server_usage import ServerUsage


T = TypeVar("T", bound="GetMcpServerUsageResponse200")


@_attrs_define
class GetMcpServerUsageResponse200:
    """
    Attributes:
        servers (list[ServerUsage]): One entry per server the caller can read, including servers with no requests
    """

    servers: list[ServerUsage]

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
        from ..models.server_usage import ServerUsage

        d = dict(src_dict)
        servers = []
        _servers = d.pop("servers")
        for servers_item_data in _servers:
            servers_item = ServerUsage.from_dict(servers_item_data)

            servers.append(servers_item)

        get_mcp_server_usage_response_200 = cls(
            servers=servers,
        )

        return get_mcp_server_usage_response_200
