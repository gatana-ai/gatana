from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_756_action import Schema756Action
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_759 import Schema759


T = TypeVar("T", bound="Schema756")


@_attrs_define
class Schema756:
    """
    Attributes:
        tools (list[str]):
        condition (str):
        action (Schema756Action): Condition actions: deny, audit or allow. Allow makes protections record matches
            without blocking or redacting. Deny rules still apply. Protection actions: block, redact or audit. Block refuses
            calls with argument matches or withholds results with matches. Redact replaces matched text. Audit records
            matches and changes nothing
        check (Schema759 | Unset):
    """

    tools: list[str]
    condition: str
    action: Schema756Action
    check: Schema759 | Unset = UNSET

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
        from ..models.schema_759 import Schema759

        d = dict(src_dict)
        tools = cast(list[str], d.pop("tools"))

        condition = d.pop("condition")

        action = Schema756Action(d.pop("action"))

        _check = d.pop("check", UNSET)
        check: Schema759 | Unset
        if isinstance(_check, Unset):
            check = UNSET
        else:
            check = Schema759.from_dict(_check)

        schema_756 = cls(
            tools=tools,
            condition=condition,
            action=action,
            check=check,
        )

        return schema_756
