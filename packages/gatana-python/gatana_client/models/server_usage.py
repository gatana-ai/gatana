from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ServerUsage")


@_attrs_define
class ServerUsage:
    """
    Attributes:
        server_id (str): ID of the server
        last_seven_days (float): MCP requests made to the server over the last seven days
    """

    server_id: str
    last_seven_days: float

    def to_dict(self) -> dict[str, Any]:
        server_id = self.server_id

        last_seven_days = self.last_seven_days

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "serverId": server_id,
                "lastSevenDays": last_seven_days,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        server_id = d.pop("serverId")

        last_seven_days = d.pop("lastSevenDays")

        server_usage = cls(
            server_id=server_id,
            last_seven_days=last_seven_days,
        )

        return server_usage
