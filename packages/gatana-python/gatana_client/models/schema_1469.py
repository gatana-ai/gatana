from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_1467 import Schema1467

T = TypeVar("T", bound="Schema1469")


@_attrs_define
class Schema1469:
    """
    Attributes:
        id (str):
        name (str):
        member_count (float):
        role (Schema1467): 'read' (the default) opens it to the principal; 'maintain' gives them the same rights as the
            creator and the organization owners
    """

    id: str
    name: str
    member_count: float
    role: Schema1467

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        member_count = self.member_count

        role = self.role.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "memberCount": member_count,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        member_count = d.pop("memberCount")

        role = Schema1467(d.pop("role"))

        schema_1469 = cls(
            id=id,
            name=name,
            member_count=member_count,
            role=role,
        )

        return schema_1469
