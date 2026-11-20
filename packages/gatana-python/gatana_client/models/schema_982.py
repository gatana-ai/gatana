from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema982")


@_attrs_define
class Schema982:
    """
    Attributes:
        percent_off (float | None): Percentage taken off the price, or null for a fixed amount
        amount_off (float | None): Fixed amount taken off the price, or null for a percentage
        ends_at (None | str): Time when the discount ends, or null if it does not end
    """

    percent_off: float | None
    amount_off: float | None
    ends_at: None | str

    def to_dict(self) -> dict[str, Any]:
        percent_off: float | None
        percent_off = self.percent_off

        amount_off: float | None
        amount_off = self.amount_off

        ends_at: None | str
        ends_at = self.ends_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "percentOff": percent_off,
                "amountOff": amount_off,
                "endsAt": ends_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_percent_off(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        percent_off = _parse_percent_off(d.pop("percentOff"))

        def _parse_amount_off(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        amount_off = _parse_amount_off(d.pop("amountOff"))

        def _parse_ends_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ends_at = _parse_ends_at(d.pop("endsAt"))

        schema_982 = cls(
            percent_off=percent_off,
            amount_off=amount_off,
            ends_at=ends_at,
        )

        return schema_982
