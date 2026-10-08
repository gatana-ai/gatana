from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema1119")


@_attrs_define
class Schema1119:
    """
    Attributes:
        id (str):
        name (str):
        member_count (float):
    """

    id: str
    name: str
    member_count: float

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        member_count = self.member_count

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "memberCount": member_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        member_count = d.pop("memberCount")

        schema_1119 = cls(
            id=id,
            name=name,
            member_count=member_count,
        )

        return schema_1119
