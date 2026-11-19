from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.activity_day import ActivityDay


T = TypeVar("T", bound="GetMcpServerDailyUsageResponse200")


@_attrs_define
class GetMcpServerDailyUsageResponse200:
    """
    Attributes:
        days (list[ActivityDay]): One entry per day of the window, including days with no calls
    """

    days: list[ActivityDay]

    def to_dict(self) -> dict[str, Any]:
        days = []
        for days_item_data in self.days:
            days_item = days_item_data.to_dict()
            days.append(days_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "days": days,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.activity_day import ActivityDay

        d = dict(src_dict)
        days = []
        _days = d.pop("days")
        for days_item_data in _days:
            days_item = ActivityDay.from_dict(days_item_data)

            days.append(days_item)

        get_mcp_server_daily_usage_response_200 = cls(
            days=days,
        )

        return get_mcp_server_daily_usage_response_200
