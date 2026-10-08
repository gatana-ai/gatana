from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="UserSmallDto")


@_attrs_define
class UserSmallDto:
    """
    Attributes:
        id (str): Unique ID of the user
        email (str): Email address of the user
        name (str): Display name of the user
    """

    id: str
    email: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "email": email,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        name = d.pop("name")

        user_small_dto = cls(
            id=id,
            email=email,
            name=name,
        )

        return user_small_dto
