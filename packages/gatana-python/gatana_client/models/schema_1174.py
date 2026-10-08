from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_1175 import Schema1175

T = TypeVar("T", bound="Schema1174")


@_attrs_define
class Schema1174:
    """
    Attributes:
        id (str):
        name (str):
        email (str):
        role (Schema1175): 'read' (the default) opens it to the principal; 'maintain' gives them the same rights as the
            creator and the organization owners
    """

    id: str
    name: str
    email: str
    role: Schema1175

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

        role = Schema1175(d.pop("role"))

        schema_1174 = cls(
            id=id,
            name=name,
            email=email,
            role=role,
        )

        return schema_1174
