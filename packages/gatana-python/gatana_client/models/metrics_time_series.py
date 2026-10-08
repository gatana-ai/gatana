from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="MetricsTimeSeries")


@_attrs_define
class MetricsTimeSeries:
    """
    Attributes:
        timestamps (list[float]): Sample times as Unix epoch timestamps in seconds
        values (list[float]): Sampled values, aligned with timestamps
    """

    timestamps: list[float]
    values: list[float]

    def to_dict(self) -> dict[str, Any]:
        timestamps = self.timestamps

        values = self.values

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "timestamps": timestamps,
                "values": values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        timestamps = cast(list[float], d.pop("timestamps"))

        values = cast(list[float], d.pop("values"))

        metrics_time_series = cls(
            timestamps=timestamps,
            values=values,
        )

        return metrics_time_series
