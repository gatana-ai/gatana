from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="TeamClaimMapping")


@_attrs_define
class TeamClaimMapping:
    """
    Attributes:
        id (str): Unique ID of the claim mapping
        tenant_id (str): ID of the tenant that owns the claim mapping
        team_id (str): ID of the team that the mapping gives membership of
        claim_key (str): Name of the identity provider claim to match
        claim_value (str): Claim value that gives membership when it matches
        created_at (str): Time when the claim mapping was created
    """

    id: str
    tenant_id: str
    team_id: str
    claim_key: str
    claim_value: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        team_id = self.team_id

        claim_key = self.claim_key

        claim_value = self.claim_value

        created_at = self.created_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "teamId": team_id,
                "claimKey": claim_key,
                "claimValue": claim_value,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        team_id = d.pop("teamId")

        claim_key = d.pop("claimKey")

        claim_value = d.pop("claimValue")

        created_at = d.pop("createdAt")

        team_claim_mapping = cls(
            id=id,
            tenant_id=tenant_id,
            team_id=team_id,
            claim_key=claim_key,
            claim_value=claim_value,
            created_at=created_at,
        )

        return team_claim_mapping
