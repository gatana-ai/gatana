from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_576 import Schema576


T = TypeVar("T", bound="CreateUserResponse")


@_attrs_define
class CreateUserResponse:
    """
    Attributes:
        user (Schema576):
        set_password_url (str | Unset):
    """

    user: Schema576
    set_password_url: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        user = self.user.to_dict()

        set_password_url = self.set_password_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "user": user,
            }
        )
        if set_password_url is not UNSET:
            field_dict["setPasswordUrl"] = set_password_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_576 import Schema576

        d = dict(src_dict)
        user = Schema576.from_dict(d.pop("user"))

        set_password_url = d.pop("setPasswordUrl", UNSET)

        create_user_response = cls(
            user=user,
            set_password_url=set_password_url,
        )

        return create_user_response
