from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_547 import Schema547
    from ..models.user_identity import UserIdentity


T = TypeVar("T", bound="GetUserMeResponse")


@_attrs_define
class GetUserMeResponse:
    """
    Attributes:
        user (Schema547): The authenticated user
        identities (list[UserIdentity]): Sign-in identities linked to the user
    """

    user: Schema547
    identities: list[UserIdentity]

    def to_dict(self) -> dict[str, Any]:
        user = self.user.to_dict()

        identities = []
        for componentsschemas_schema567_item_data in self.identities:
            componentsschemas_schema567_item = componentsschemas_schema567_item_data.to_dict()
            identities.append(componentsschemas_schema567_item)

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
        from ..models.schema_547 import Schema547
        from ..models.user_identity import UserIdentity

        d = dict(src_dict)
        user = Schema547.from_dict(d.pop("user"))

        identities = []
        _identities = d.pop("identities")
        for componentsschemas_schema567_item_data in _identities:
            componentsschemas_schema567_item = UserIdentity.from_dict(componentsschemas_schema567_item_data)

            identities.append(componentsschemas_schema567_item)

        get_user_me_response = cls(
            user=user,
            identities=identities,
        )

        return get_user_me_response
