from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema658")


@_attrs_define
class Schema658:
    """
    Attributes:
        success (bool):
        error (str):
    """

    success: bool
    error: str

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        error = self.error

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "success": success,
                "error": error,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        error = d.pop("error")

        schema_658 = cls(
            success=success,
            error=error,
        )

        return schema_658
