from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.team_invitation import TeamInvitation


T = TypeVar("T", bound="CreateTeamInvitationResponse200")


@_attrs_define
class CreateTeamInvitationResponse200:
    """
    Attributes:
        invitation (TeamInvitation):
    """

    invitation: TeamInvitation

    def to_dict(self) -> dict[str, Any]:
        invitation = self.invitation.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitation": invitation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_invitation import TeamInvitation

        d = dict(src_dict)
        invitation = TeamInvitation.from_dict(d.pop("invitation"))

        create_team_invitation_response_200 = cls(
            invitation=invitation,
        )

        return create_team_invitation_response_200
