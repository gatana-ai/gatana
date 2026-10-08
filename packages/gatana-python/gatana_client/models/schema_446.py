from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="Schema446")


@_attrs_define
class Schema446:
    """
    Attributes:
        user (User):
    """

    user: User

    def to_dict(self) -> dict[str, Any]:
        user = self.user.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        user = User.from_dict(d.pop("user"))

        schema_446 = cls(
            user=user,
        )

        return schema_446
