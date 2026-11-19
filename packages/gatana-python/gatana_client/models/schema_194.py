from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_194_action import Schema194Action
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_197 import Schema197


T = TypeVar("T", bound="Schema194")


@_attrs_define
class Schema194:
    """
    Attributes:
        action (Schema194Action): Condition actions: deny, audit or allow. Allow makes protections record matches
            without blocking or redacting. Deny rules still apply. Protection actions: block, redact or audit. Block refuses
            calls with argument matches or withholds results with matches. Redact replaces matched text. Audit records
            matches and changes nothing
        tools (list[str] | Unset):
        condition (str | Unset):
        check (Schema197 | Unset):
    """

    action: Schema194Action
    tools: list[str] | Unset = UNSET
    condition: str | Unset = UNSET
    check: Schema197 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action.value

        tools: list[str] | Unset = UNSET
        if not isinstance(self.tools, Unset):
            tools = self.tools

        condition = self.condition

        check: dict[str, Any] | Unset = UNSET
        if not isinstance(self.check, Unset):
            check = self.check.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
            }
        )
        if tools is not UNSET:
            field_dict["tools"] = tools
        if condition is not UNSET:
            field_dict["condition"] = condition
        if check is not UNSET:
            field_dict["check"] = check

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_197 import Schema197

        d = dict(src_dict)
        action = Schema194Action(d.pop("action"))

        tools = cast(list[str], d.pop("tools", UNSET))

        condition = d.pop("condition", UNSET)

        _check = d.pop("check", UNSET)
        check: Schema197 | Unset
        if isinstance(_check, Unset):
            check = UNSET
        else:
            check = Schema197.from_dict(_check)

        schema_194 = cls(
            action=action,
            tools=tools,
            condition=condition,
            check=check,
        )

        schema_194.additional_properties = d
        return schema_194

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
