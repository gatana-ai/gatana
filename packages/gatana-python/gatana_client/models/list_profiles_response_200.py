from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.profile_list_item_dto import ProfileListItemDto


T = TypeVar("T", bound="ListProfilesResponse200")


@_attrs_define
class ListProfilesResponse200:
    """
    Attributes:
        profiles (list[ProfileListItemDto]):
    """

    profiles: list[ProfileListItemDto]

    def to_dict(self) -> dict[str, Any]:
        profiles = []
        for profiles_item_data in self.profiles:
            profiles_item = profiles_item_data.to_dict()
            profiles.append(profiles_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "profiles": profiles,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_list_item_dto import ProfileListItemDto

        d = dict(src_dict)
        profiles = []
        _profiles = d.pop("profiles")
        for profiles_item_data in _profiles:
            profiles_item = ProfileListItemDto.from_dict(profiles_item_data)

            profiles.append(profiles_item)

        list_profiles_response_200 = cls(
            profiles=profiles,
        )

        return list_profiles_response_200
