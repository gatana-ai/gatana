from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.protection_check_target import ProtectionCheckTarget
from ..models.protection_check_type import ProtectionCheckType

T = TypeVar("T", bound="Schema752")


@_attrs_define
class Schema752:
    """
    Attributes:
        type_ (ProtectionCheckType):
        target (ProtectionCheckTarget):
    """

    type_: ProtectionCheckType
    target: ProtectionCheckTarget

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        target = self.target.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "target": target,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = ProtectionCheckType(d.pop("type"))

        target = ProtectionCheckTarget(d.pop("target"))

        schema_752 = cls(
            type_=type_,
            target=target,
        )

        return schema_752
