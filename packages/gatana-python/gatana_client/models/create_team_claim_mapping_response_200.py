from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.team_claim_mapping import TeamClaimMapping


T = TypeVar("T", bound="CreateTeamClaimMappingResponse200")


@_attrs_define
class CreateTeamClaimMappingResponse200:
    """
    Attributes:
        claim_mapping (TeamClaimMapping):
    """

    claim_mapping: TeamClaimMapping

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
        from ..models.team_claim_mapping import TeamClaimMapping

        d = dict(src_dict)
        claim_mapping = TeamClaimMapping.from_dict(d.pop("claimMapping"))

        create_team_claim_mapping_response_200 = cls(
            claim_mapping=claim_mapping,
        )

        return create_team_claim_mapping_response_200
