from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.team_with_member_count import TeamWithMemberCount


T = TypeVar("T", bound="Schema878")


@_attrs_define
class Schema878:
    """
    Attributes:
        team (TeamWithMemberCount):
    """

    team: TeamWithMemberCount

    def to_dict(self) -> dict[str, Any]:
        team = self.team.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "team": team,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_with_member_count import TeamWithMemberCount

        d = dict(src_dict)
        team = TeamWithMemberCount.from_dict(d.pop("team"))

        schema_878 = cls(
            team=team,
        )

        return schema_878
