from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="ListUsersResponse200")


@_attrs_define
class ListUsersResponse200:
    """
    Attributes:
        users (list[User]): Users and service accounts the caller can read
    """

    users: list[User]

    def to_dict(self) -> dict[str, Any]:
        users = []
        for users_item_data in self.users:
            users_item = users_item_data.to_dict()
            users.append(users_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "users": users,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for users_item_data in _users:
            users_item = User.from_dict(users_item_data)

            users.append(users_item)

        list_users_response_200 = cls(
            users=users,
        )

        return list_users_response_200
