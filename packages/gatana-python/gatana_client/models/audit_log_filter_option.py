from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuditLogFilterOption")


@_attrs_define
class AuditLogFilterOption:
    """
    Attributes:
        value (str): Value to filter by
        label (str): How the value reads to a person
        sublabel (str | Unset):
    """

    value: str
    label: str
    sublabel: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        label = self.label

        sublabel = self.sublabel

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "value": value,
                "label": label,
            }
        )
        if sublabel is not UNSET:
            field_dict["sublabel"] = sublabel

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        label = d.pop("label")

        sublabel = d.pop("sublabel", UNSET)

        audit_log_filter_option = cls(
            value=value,
            label=label,
            sublabel=sublabel,
        )

        return audit_log_filter_option
