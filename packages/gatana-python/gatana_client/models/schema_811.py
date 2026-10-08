from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.metrics_time_series import MetricsTimeSeries


T = TypeVar("T", bound="Schema811")


@_attrs_define
class Schema811:
    """
    Attributes:
        usage (MetricsTimeSeries):
        capacity_bytes (float | None): Size the volume asks for in bytes, or null when unknown
    """

    usage: MetricsTimeSeries
    capacity_bytes: float | None

    def to_dict(self) -> dict[str, Any]:
        usage = self.usage.to_dict()

        capacity_bytes: float | None
        capacity_bytes = self.capacity_bytes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "usage": usage,
                "capacityBytes": capacity_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metrics_time_series import MetricsTimeSeries

        d = dict(src_dict)
        usage = MetricsTimeSeries.from_dict(d.pop("usage"))

        def _parse_capacity_bytes(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        capacity_bytes = _parse_capacity_bytes(d.pop("capacityBytes"))

        schema_811 = cls(
            usage=usage,
            capacity_bytes=capacity_bytes,
        )

        return schema_811
