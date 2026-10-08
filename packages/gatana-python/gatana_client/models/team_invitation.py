from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_892 import Schema892

T = TypeVar("T", bound="TeamInvitation")


@_attrs_define
class TeamInvitation:
    """
    Attributes:
        id (str): Unique ID of the invitation
        team_id (str): ID of the team the invitation is for
        tenant_id (str): ID of the tenant that owns the invitation
        inviter_user_id (None | str): ID of the user who sent the invitation, or null
        email (str): Email address the invitation was sent to
        role (Schema892):
        token (str): Token used to accept the invitation
        expires_at (str): Time when the invitation expires
        accepted_at (None | str): Time when the invitation was accepted, or null
        created_at (str): Time when the invitation was created
        updated_at (str): Time when the invitation was last updated
    """

    id: str
    team_id: str
    tenant_id: str
    inviter_user_id: None | str
    email: str
    role: Schema892
    token: str
    expires_at: str
    accepted_at: None | str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        team_id = self.team_id

        tenant_id = self.tenant_id

        inviter_user_id: None | str
        inviter_user_id = self.inviter_user_id

        email = self.email

        role = self.role.value

        token = self.token

        expires_at = self.expires_at

        accepted_at: None | str
        accepted_at = self.accepted_at

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "teamId": team_id,
                "tenantId": tenant_id,
                "inviterUserId": inviter_user_id,
                "email": email,
                "role": role,
                "token": token,
                "expiresAt": expires_at,
                "acceptedAt": accepted_at,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        team_id = d.pop("teamId")

        tenant_id = d.pop("tenantId")

        def _parse_inviter_user_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        inviter_user_id = _parse_inviter_user_id(d.pop("inviterUserId"))

        email = d.pop("email")

        role = Schema892(d.pop("role"))

        token = d.pop("token")

        expires_at = d.pop("expiresAt")

        def _parse_accepted_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        accepted_at = _parse_accepted_at(d.pop("acceptedAt"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        team_invitation = cls(
            id=id,
            team_id=team_id,
            tenant_id=tenant_id,
            inviter_user_id=inviter_user_id,
            email=email,
            role=role,
            token=token,
            expires_at=expires_at,
            accepted_at=accepted_at,
            created_at=created_at,
            updated_at=updated_at,
        )

        return team_invitation
