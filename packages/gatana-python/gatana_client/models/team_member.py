from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_882 import Schema882

T = TypeVar("T", bound="TeamMember")


@_attrs_define
class TeamMember:
    """
    Attributes:
        team_id (str): ID of the team
        user_id (str): ID of the member user
        role (Schema882):
        created_at (str): Time when the membership was created
        updated_at (str): Time when the membership was last updated
    """

    team_id: str
    user_id: str
    role: Schema882
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        team_id = self.team_id

        user_id = self.user_id

        role = self.role.value

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "teamId": team_id,
                "userId": user_id,
                "role": role,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team_id = d.pop("teamId")

        user_id = d.pop("userId")

        role = Schema882(d.pop("role"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        team_member = cls(
            team_id=team_id,
            user_id=user_id,
            role=role,
            created_at=created_at,
            updated_at=updated_at,
        )

        return team_member
