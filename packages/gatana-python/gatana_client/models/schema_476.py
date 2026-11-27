from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_473 import Schema473
from ..models.schema_474 import Schema474
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema476")


@_attrs_define
class Schema476:
    """
    Attributes:
        status (Schema473): available: the organization can use it. upgrade: the plan does not include it. unavailable:
            the installation cannot run it
        reason (Schema474 | Unset): The service or resource missing from the installation
    """

    status: Schema473
    reason: Schema474 | Unset = UNSET

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
        status = Schema473(d.pop("status"))

        _reason = d.pop("reason", UNSET)
        reason: Schema474 | Unset
        if isinstance(_reason, Unset):
            reason = UNSET
        else:
            reason = Schema474(_reason)

        schema_476 = cls(
            status=status,
            reason=reason,
        )

        return schema_476
