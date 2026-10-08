from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.team_claim_mapping import TeamClaimMapping


T = TypeVar("T", bound="ListTeamClaimMappingsResponse200")


@_attrs_define
class ListTeamClaimMappingsResponse200:
    """
    Attributes:
        claim_mappings (list[TeamClaimMapping]): Claim mappings of the team
    """

    claim_mappings: list[TeamClaimMapping]

    def to_dict(self) -> dict[str, Any]:
        claim_mappings = []
        for claim_mappings_item_data in self.claim_mappings:
            claim_mappings_item = claim_mappings_item_data.to_dict()
            claim_mappings.append(claim_mappings_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "claimMappings": claim_mappings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_claim_mapping import TeamClaimMapping

        d = dict(src_dict)
        claim_mappings = []
        _claim_mappings = d.pop("claimMappings")
        for claim_mappings_item_data in _claim_mappings:
            claim_mappings_item = TeamClaimMapping.from_dict(claim_mappings_item_data)

            claim_mappings.append(claim_mappings_item)

        list_team_claim_mappings_response_200 = cls(
            claim_mappings=claim_mappings,
        )

        return list_team_claim_mappings_response_200
