from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.activity_caller import ActivityCaller
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
        callers (list[ActivityCaller]): The most used clients and tokens, busiest first
    """

    days: list[ActivityDay]
    total: float
    servers: list[ActivityServer]
    callers: list[ActivityCaller]

    def to_dict(self) -> dict[str, Any]:
        days = []
        for componentsschemas_schema382_item_data in self.days:
            componentsschemas_schema382_item = componentsschemas_schema382_item_data.to_dict()
            days.append(componentsschemas_schema382_item)

        total = self.total

        servers = []
        for componentsschemas_schema386_item_data in self.servers:
            componentsschemas_schema386_item = componentsschemas_schema386_item_data.to_dict()
            servers.append(componentsschemas_schema386_item)

        callers = []
        for componentsschemas_schema390_item_data in self.callers:
            componentsschemas_schema390_item = componentsschemas_schema390_item_data.to_dict()
            callers.append(componentsschemas_schema390_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "days": days,
                "total": total,
                "servers": servers,
                "callers": callers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.activity_caller import ActivityCaller
        from ..models.activity_day import ActivityDay
        from ..models.activity_server import ActivityServer

        d = dict(src_dict)
        days = []
        _days = d.pop("days")
        for componentsschemas_schema382_item_data in _days:
            componentsschemas_schema382_item = ActivityDay.from_dict(componentsschemas_schema382_item_data)

            days.append(componentsschemas_schema382_item)

        total = d.pop("total")

        servers = []
        _servers = d.pop("servers")
        for componentsschemas_schema386_item_data in _servers:
            componentsschemas_schema386_item = ActivityServer.from_dict(componentsschemas_schema386_item_data)

            servers.append(componentsschemas_schema386_item)

        callers = []
        _callers = d.pop("callers")
        for componentsschemas_schema390_item_data in _callers:
            componentsschemas_schema390_item = ActivityCaller.from_dict(componentsschemas_schema390_item_data)

            callers.append(componentsschemas_schema390_item)

        activity_summary = cls(
            days=days,
            total=total,
            servers=servers,
            callers=callers,
        )

        return activity_summary
