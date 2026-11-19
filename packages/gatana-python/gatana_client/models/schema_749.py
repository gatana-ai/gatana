from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_749_action import Schema749Action
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_752 import Schema752


T = TypeVar("T", bound="Schema749")


@_attrs_define
class Schema749:
    """
    Attributes:
        tools (list[str]):
        condition (str):
        action (Schema749Action): Condition actions: deny, audit or allow. Allow makes protections record matches
            without blocking or redacting. Deny rules still apply. Protection actions: block, redact or audit. Block refuses
            calls with argument matches or withholds results with matches. Redact replaces matched text. Audit records
            matches and changes nothing
        check (Schema752 | Unset):
    """

    tools: list[str]
    condition: str
    action: Schema749Action
    check: Schema752 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        tools = self.tools

        condition = self.condition

        action = self.action.value

        check: dict[str, Any] | Unset = UNSET
        if not isinstance(self.check, Unset):
            check = self.check.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tools": tools,
                "condition": condition,
                "action": action,
            }
        )
        if check is not UNSET:
            field_dict["check"] = check

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_752 import Schema752

        d = dict(src_dict)
        tools = cast(list[str], d.pop("tools"))

        condition = d.pop("condition")

        action = Schema749Action(d.pop("action"))

        _check = d.pop("check", UNSET)
        check: Schema752 | Unset
        if isinstance(_check, Unset):
            check = UNSET
        else:
            check = Schema752.from_dict(_check)

        schema_749 = cls(
            tools=tools,
            condition=condition,
            action=action,
            check=check,
        )

        return schema_749
