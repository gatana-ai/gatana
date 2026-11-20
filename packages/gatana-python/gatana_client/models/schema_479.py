from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_472 import Schema472
from ..models.schema_473 import Schema473
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema479")


@_attrs_define
class Schema479:
    """
    Attributes:
        status (Schema472): available: the organization can use it. upgrade: the plan does not include it. unavailable:
            the installation cannot run it
        reason (Schema473 | Unset): The service or resource missing from the installation
    """

    status: Schema472
    reason: Schema473 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        reason: str | Unset = UNSET
        if not isinstance(self.reason, Unset):
            reason = self.reason.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "status": status,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = Schema472(d.pop("status"))

        _reason = d.pop("reason", UNSET)
        reason: Schema473 | Unset
        if isinstance(_reason, Unset):
            reason = UNSET
        else:
            reason = Schema473(_reason)

        schema_479 = cls(
            status=status,
            reason=reason,
        )

        return schema_479
