from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_938 import Schema938


T = TypeVar("T", bound="ListTeamMembersResponse200")


@_attrs_define
class ListTeamMembersResponse200:
    """
    Attributes:
        members (list[Schema938]): Members of the team
    """

    members: list[Schema938]

    def to_dict(self) -> dict[str, Any]:
        members = []
        for members_item_data in self.members:
            members_item = members_item_data.to_dict()
            members.append(members_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "members": members,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_938 import Schema938

        d = dict(src_dict)
        members = []
        _members = d.pop("members")
        for members_item_data in _members:
            members_item = Schema938.from_dict(members_item_data)

            members.append(members_item)

        list_team_members_response_200 = cls(
            members=members,
        )

        return list_team_members_response_200
