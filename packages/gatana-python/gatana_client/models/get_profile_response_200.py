from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.profile_details_dto import ProfileDetailsDto


T = TypeVar("T", bound="GetProfileResponse200")


@_attrs_define
class GetProfileResponse200:
    """
    Attributes:
        profile (ProfileDetailsDto):
    """

    profile: ProfileDetailsDto

    def to_dict(self) -> dict[str, Any]:
        profile = self.profile.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "profile": profile,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_details_dto import ProfileDetailsDto

        d = dict(src_dict)
        profile = ProfileDetailsDto.from_dict(d.pop("profile"))

        get_profile_response_200 = cls(
            profile=profile,
        )

        return get_profile_response_200
