from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_1271 import Schema1271

T = TypeVar("T", bound="Schema1270")


@_attrs_define
class Schema1270:
    """
    Attributes:
        id (str):
        name (str):
        email (str):
        role (Schema1271): 'read' (the default) opens it to the principal; 'maintain' gives them the same rights as the
            creator and the organization owners
    """

    id: str
    name: str
    email: str
    role: Schema1271

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        email = self.email

        role = self.role.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "email": email,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        email = d.pop("email")

        role = Schema1271(d.pop("role"))

        schema_1270 = cls(
            id=id,
            name=name,
            email=email,
            role=role,
        )

        return schema_1270
