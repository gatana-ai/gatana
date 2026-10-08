from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.team_member import TeamMember
    from ..models.user import User


T = TypeVar("T", bound="Schema879")


@_attrs_define
class Schema879:
    """
    Attributes:
        member (TeamMember):
        user (User):
    """

    member: TeamMember
    user: User

    def to_dict(self) -> dict[str, Any]:
        member = self.member.to_dict()

        user = self.user.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "member": member,
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_member import TeamMember
        from ..models.user import User

        d = dict(src_dict)
        member = TeamMember.from_dict(d.pop("member"))

        user = User.from_dict(d.pop("user"))

        schema_879 = cls(
            member=member,
            user=user,
        )

        return schema_879
