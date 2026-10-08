from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ActivityDay")


@_attrs_define
class ActivityDay:
    """
    Attributes:
        date (str): The day, as YYYY-MM-DD, cut in the time zone the summary was asked for
        count (float): Tool calls made that day
    """

    date: str
    count: float

    def to_dict(self) -> dict[str, Any]:
        date = self.date

        count = self.count

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "date": date,
                "count": count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date = d.pop("date")

        count = d.pop("count")

        activity_day = cls(
            date=date,
            count=count,
        )

        return activity_day
