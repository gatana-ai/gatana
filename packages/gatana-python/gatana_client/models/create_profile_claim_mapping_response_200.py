from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.profile_claim_mapping import ProfileClaimMapping


T = TypeVar("T", bound="CreateProfileClaimMappingResponse200")


@_attrs_define
class CreateProfileClaimMappingResponse200:
    """
    Attributes:
        claim_mapping (ProfileClaimMapping):
    """

    claim_mapping: ProfileClaimMapping

    def to_dict(self) -> dict[str, Any]:
        claim_mapping = self.claim_mapping.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "claimMapping": claim_mapping,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_claim_mapping import ProfileClaimMapping

        d = dict(src_dict)
        claim_mapping = ProfileClaimMapping.from_dict(d.pop("claimMapping"))

        create_profile_claim_mapping_response_200 = cls(
            claim_mapping=claim_mapping,
        )

        return create_profile_claim_mapping_response_200
