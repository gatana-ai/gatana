from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.activity_day import ActivityDay
    from ..models.activity_server import ActivityServer


T = TypeVar("T", bound="ActivitySummary")


@_attrs_define
class ActivitySummary:
    """
    Attributes:
        days (list[ActivityDay]): One entry per day of the window, including days with no calls
        total (float): Tool calls over the whole window
        servers (list[ActivityServer]): The most used servers, busiest first
    """

    days: list[ActivityDay]
    total: float
    servers: list[ActivityServer]

    def to_dict(self) -> dict[str, Any]:
        days = []
        for componentsschemas_schema435_item_data in self.days:
            componentsschemas_schema435_item = componentsschemas_schema435_item_data.to_dict()
            days.append(componentsschemas_schema435_item)

        total = self.total

        servers = []
        for componentsschemas_schema439_item_data in self.servers:
            componentsschemas_schema439_item = componentsschemas_schema439_item_data.to_dict()
            servers.append(componentsschemas_schema439_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "days": days,
                "total": total,
                "servers": servers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.activity_day import ActivityDay
        from ..models.activity_server import ActivityServer

        d = dict(src_dict)
        days = []
        _days = d.pop("days")
        for componentsschemas_schema435_item_data in _days:
            componentsschemas_schema435_item = ActivityDay.from_dict(componentsschemas_schema435_item_data)

            days.append(componentsschemas_schema435_item)

        total = d.pop("total")

        servers = []
        _servers = d.pop("servers")
        for componentsschemas_schema439_item_data in _servers:
            componentsschemas_schema439_item = ActivityServer.from_dict(componentsschemas_schema439_item_data)

            servers.append(componentsschemas_schema439_item)

        activity_summary = cls(
            days=days,
            total=total,
            servers=servers,
        )

        return activity_summary
