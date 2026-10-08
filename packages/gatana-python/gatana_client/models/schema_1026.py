from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema1026")


@_attrs_define
class Schema1026:
    """
    Attributes:
        id (str): Unique ID of the user
        email (str): Email address of the user
        name (str): Display name of the user
        added_at (str): Time when the maintainer was added
    """

    id: str
    email: str
    name: str
    added_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        name = self.name

        added_at = self.added_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "email": email,
                "name": name,
                "addedAt": added_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        name = d.pop("name")

        added_at = d.pop("addedAt")

        schema_1026 = cls(
            id=id,
            email=email,
            name=name,
            added_at=added_at,
        )

        return schema_1026
