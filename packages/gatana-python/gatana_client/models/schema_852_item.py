from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_484 import Schema484

T = TypeVar("T", bound="Schema852Item")


@_attrs_define
class Schema852Item:
    """
    Attributes:
        role (Schema484):
        id (str):
        name (str):
        email (str):
    """

    role: Schema484
    id: str
    name: str
    email: str

    def to_dict(self) -> dict[str, Any]:
        role = self.role.value

        id = self.id

        name = self.name

        email = self.email

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "role": role,
                "id": id,
                "name": name,
                "email": email,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = Schema484(d.pop("role"))

        id = d.pop("id")

        name = d.pop("name")

        email = d.pop("email")

        schema_852_item = cls(
            role=role,
            id=id,
            name=name,
            email=email,
        )

        return schema_852_item
