from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema1117")


@_attrs_define
class Schema1117:
    """
    Attributes:
        id (str):
        name (str):
        email (str):
    """

    id: str
    name: str
    email: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        email = self.email

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "email": email,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        email = d.pop("email")

        schema_1117 = cls(
            id=id,
            name=name,
            email=email,
        )

        return schema_1117
