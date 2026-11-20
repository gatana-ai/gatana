from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_578 import Schema578


T = TypeVar("T", bound="GetUserResponse200")


@_attrs_define
class GetUserResponse200:
    """
    Attributes:
        user (Schema578):
        last_active_at (None | str): Last request time through a connected client or personal access token, or null if
            none exists or the caller cannot update the user
    """

    user: Schema578
    last_active_at: None | str

    def to_dict(self) -> dict[str, Any]:
        user = self.user.to_dict()

        last_active_at: None | str
        last_active_at = self.last_active_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "user": user,
                "lastActiveAt": last_active_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_578 import Schema578

        d = dict(src_dict)
        user = Schema578.from_dict(d.pop("user"))

        def _parse_last_active_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_active_at = _parse_last_active_at(d.pop("lastActiveAt"))

        get_user_response_200 = cls(
            user=user,
            last_active_at=last_active_at,
        )

        return get_user_response_200
