from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_575 import Schema575


T = TypeVar("T", bound="UpdateUserResponse200")


@_attrs_define
class UpdateUserResponse200:
    """
    Attributes:
        user (Schema575):
    """

    user: Schema575

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
        from ..models.schema_575 import Schema575

        d = dict(src_dict)
        user = Schema575.from_dict(d.pop("user"))

        update_user_response_200 = cls(
            user=user,
        )

        return update_user_response_200
