from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_353 import Schema353

T = TypeVar("T", bound="Schema628Item")


@_attrs_define
class Schema628Item:
    """
    Attributes:
        role (Schema353):
        id (str):
        name (str):
    """

    role: Schema353
    id: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        role = self.role.value

        id = self.id

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "role": role,
                "id": id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = Schema353(d.pop("role"))

        id = d.pop("id")

        name = d.pop("name")

        schema_628_item = cls(
            role=role,
            id=id,
            name=name,
        )

        return schema_628_item
