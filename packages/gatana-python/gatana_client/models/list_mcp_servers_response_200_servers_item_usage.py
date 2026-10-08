from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ListMcpServersResponse200ServersItemUsage")


@_attrs_define
class ListMcpServersResponse200ServersItemUsage:
    """
    Attributes:
        last_seven_days (float):
    """

    last_seven_days: float

    def to_dict(self) -> dict[str, Any]:
        last_seven_days = self.last_seven_days

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "lastSevenDays": last_seven_days,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        last_seven_days = d.pop("lastSevenDays")

        list_mcp_servers_response_200_servers_item_usage = cls(
            last_seven_days=last_seven_days,
        )

        return list_mcp_servers_response_200_servers_item_usage
