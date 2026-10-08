from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema755")


@_attrs_define
class Schema755:
    """
    Attributes:
        valid (bool): Whether the card is valid
        brand (str): Card brand (e.g. "visa")
        last4 (str): Last four digits of the card number
        expires_year (float): Year the card expires
        expires_month (float): Month the card expires
    """

    valid: bool
    brand: str
    last4: str
    expires_year: float
    expires_month: float

    def to_dict(self) -> dict[str, Any]:
        valid = self.valid

        brand = self.brand

        last4 = self.last4

        expires_year = self.expires_year

        expires_month = self.expires_month

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "valid": valid,
                "brand": brand,
                "last4": last4,
                "expiresYear": expires_year,
                "expiresMonth": expires_month,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        valid = d.pop("valid")

        brand = d.pop("brand")

        last4 = d.pop("last4")

        expires_year = d.pop("expiresYear")

        expires_month = d.pop("expiresMonth")

        schema_755 = cls(
            valid=valid,
            brand=brand,
            last4=last4,
            expires_year=expires_year,
            expires_month=expires_month,
        )

        return schema_755
