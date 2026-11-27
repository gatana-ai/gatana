from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.protection_on_action import ProtectionOnAction
from ..models.protection_value_source import ProtectionValueSource
from ..models.schema_775 import Schema775

T = TypeVar("T", bound="ResolvedProtectionAction")


@_attrs_define
class ResolvedProtectionAction:
    """
    Attributes:
        action (ProtectionOnAction):
        source (ProtectionValueSource):
        inherited (Schema775):
    """

    action: ProtectionOnAction
    source: ProtectionValueSource
    inherited: Schema775

    def to_dict(self) -> dict[str, Any]:
        action = self.action.value

        source = self.source.value

        inherited = self.inherited.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "action": action,
                "source": source,
                "inherited": inherited,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action = ProtectionOnAction(d.pop("action"))

        source = ProtectionValueSource(d.pop("source"))

        inherited = Schema775(d.pop("inherited"))

        resolved_protection_action = cls(
            action=action,
            source=source,
            inherited=inherited,
        )

        return resolved_protection_action
