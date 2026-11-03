from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_718_action import Schema718Action

T = TypeVar("T", bound="Schema718")


@_attrs_define
class Schema718:
    """
    Attributes:
        condition (str): CEL representing the condition
        action (Schema718Action): Action to take when the condition matches
    """

    condition: str
    action: Schema718Action

    def to_dict(self) -> dict[str, Any]:
        condition = self.condition

        action = self.action.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "condition": condition,
                "action": action,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        condition = d.pop("condition")

        action = Schema718Action(d.pop("action"))

        schema_718 = cls(
            condition=condition,
            action=action,
        )

        return schema_718
