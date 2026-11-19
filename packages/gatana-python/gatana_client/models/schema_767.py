from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.protection_on_action import ProtectionOnAction
from ..models.protection_value_source import ProtectionValueSource
from ..models.schema_768 import Schema768

T = TypeVar("T", bound="Schema767")


@_attrs_define
class Schema767:
    """
    Attributes:
        action (ProtectionOnAction):
        source (ProtectionValueSource):
        inherited (Schema768):
    """

    action: ProtectionOnAction
    source: ProtectionValueSource
    inherited: Schema768

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

        inherited = Schema768(d.pop("inherited"))

        schema_767 = cls(
            action=action,
            source=source,
            inherited=inherited,
        )

        return schema_767
