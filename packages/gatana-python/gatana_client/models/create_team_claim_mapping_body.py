from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateTeamClaimMappingBody")


@_attrs_define
class CreateTeamClaimMappingBody:
    """
    Attributes:
        claim_key (str): Name of the identity provider claim to match
        claim_value (str): Claim value that gives membership when it matches
    """

    claim_key: str
    claim_value: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        claim_key = self.claim_key

        claim_value = self.claim_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "claimKey": claim_key,
                "claimValue": claim_value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        claim_key = d.pop("claimKey")

        claim_value = d.pop("claimValue")

        create_team_claim_mapping_body = cls(
            claim_key=claim_key,
            claim_value=claim_value,
        )

        create_team_claim_mapping_body.additional_properties = d
        return create_team_claim_mapping_body

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
