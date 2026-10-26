from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_625_action import Schema625Action

T = TypeVar("T", bound="Schema625")


@_attrs_define
class Schema625:
    """
    Attributes:
        condition (str): CEL representing the condition
        action (Schema625Action): Action to take when the condition matches
    """

    condition: str
    action: Schema625Action

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

        action = Schema625Action(d.pop("action"))

        schema_625 = cls(
            condition=condition,
            action=action,
        )

        return schema_625
