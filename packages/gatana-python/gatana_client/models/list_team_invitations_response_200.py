from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.team_invitation import TeamInvitation


T = TypeVar("T", bound="ListTeamInvitationsResponse200")


@_attrs_define
class ListTeamInvitationsResponse200:
    """
    Attributes:
        invitations (list[TeamInvitation]): Invitations of the team
    """

    invitations: list[TeamInvitation]

    def to_dict(self) -> dict[str, Any]:
        invitations = []
        for invitations_item_data in self.invitations:
            invitations_item = invitations_item_data.to_dict()
            invitations.append(invitations_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitations": invitations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_invitation import TeamInvitation

        d = dict(src_dict)
        invitations = []
        _invitations = d.pop("invitations")
        for invitations_item_data in _invitations:
            invitations_item = TeamInvitation.from_dict(invitations_item_data)

            invitations.append(invitations_item)

        list_team_invitations_response_200 = cls(
            invitations=invitations,
        )

        return list_team_invitations_response_200
