from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema626")


@_attrs_define
class Schema626:
    """
    Attributes:
        success (bool):
        message (str):
    """

    success: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "success": success,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        schema_626 = cls(
            success=success,
            message=message,
        )

        return schema_626
