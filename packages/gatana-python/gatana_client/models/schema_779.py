from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.protection_value_source import ProtectionValueSource

T = TypeVar("T", bound="Schema779")


@_attrs_define
class Schema779:
    """
    Attributes:
        value (Any):
        source (ProtectionValueSource):
        inherited (Any): The value used when the server has no override
    """

    value: Any
    source: ProtectionValueSource
    inherited: Any

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        source = self.source.value

        inherited = self.inherited

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "value": value,
                "source": source,
                "inherited": inherited,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        source = ProtectionValueSource(d.pop("source"))

        inherited = d.pop("inherited")

        schema_779 = cls(
            value=value,
            source=source,
            inherited=inherited,
        )

        return schema_779
