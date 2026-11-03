from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_449 import Schema449
from ..models.schema_450 import Schema450
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema451")


@_attrs_define
class Schema451:
    """
    Attributes:
        status (Schema449): available: the organization can use it. upgrade: the plan does not include it. unavailable:
            the installation cannot run it
        reason (Schema450 | Unset): The service or resource missing from the installation
    """

    status: Schema449
    reason: Schema450 | Unset = UNSET

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
        status = Schema449(d.pop("status"))

        _reason = d.pop("reason", UNSET)
        reason: Schema450 | Unset
        if isinstance(_reason, Unset):
            reason = UNSET
        else:
            reason = Schema450(_reason)

        schema_451 = cls(
            status=status,
            reason=reason,
        )

        return schema_451
