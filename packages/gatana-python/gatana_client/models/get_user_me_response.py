from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_418 import Schema418
    from ..models.user_identity import UserIdentity


T = TypeVar("T", bound="GetUserMeResponse")


@_attrs_define
class GetUserMeResponse:
    """
    Attributes:
        user (Schema418): The authenticated user
        identities (list[UserIdentity]): Sign-in identities linked to the user
    """

    user: Schema418
    identities: list[UserIdentity]

    def to_dict(self) -> dict[str, Any]:
        user = self.user.to_dict()

        identities = []
        for componentsschemas_schema438_item_data in self.identities:
            componentsschemas_schema438_item = componentsschemas_schema438_item_data.to_dict()
            identities.append(componentsschemas_schema438_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "user": user,
                "identities": identities,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_418 import Schema418
        from ..models.user_identity import UserIdentity

        d = dict(src_dict)
        user = Schema418.from_dict(d.pop("user"))

        identities = []
        _identities = d.pop("identities")
        for componentsschemas_schema438_item_data in _identities:
            componentsschemas_schema438_item = UserIdentity.from_dict(componentsschemas_schema438_item_data)

            identities.append(componentsschemas_schema438_item)

        get_user_me_response = cls(
            user=user,
            identities=identities,
        )

        return get_user_me_response
