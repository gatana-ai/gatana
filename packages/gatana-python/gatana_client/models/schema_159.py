from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_159_action import Schema159Action

T = TypeVar("T", bound="Schema159")


@_attrs_define
class Schema159:
    """
    Attributes:
        condition (str): CEL representing the condition
        action (Schema159Action): Action to take when the condition matches
    """

    condition: str
    action: Schema159Action
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        condition = self.condition

        action = self.action.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
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

        action = Schema159Action(d.pop("action"))

        schema_159 = cls(
            condition=condition,
            action=action,
        )

        schema_159.additional_properties = d
        return schema_159

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
