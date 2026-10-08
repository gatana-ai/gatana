from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1174 import Schema1174
    from ..models.schema_1177 import Schema1177


T = TypeVar("T", bound="SkillCollectionSharesResponse")


@_attrs_define
class SkillCollectionSharesResponse:
    """
    Attributes:
        users (list[Schema1174]): User accounts with access, oldest share first
        teams (list[Schema1177]): Teams with access, oldest share first; every member of a team has it
    """

    users: list[Schema1174]
    teams: list[Schema1177]

    def to_dict(self) -> dict[str, Any]:
        users = []
        for componentsschemas_schema1173_item_data in self.users:
            componentsschemas_schema1173_item = componentsschemas_schema1173_item_data.to_dict()
            users.append(componentsschemas_schema1173_item)

        teams = []
        for componentsschemas_schema1176_item_data in self.teams:
            componentsschemas_schema1176_item = componentsschemas_schema1176_item_data.to_dict()
            teams.append(componentsschemas_schema1176_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "users": users,
                "teams": teams,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1174 import Schema1174
        from ..models.schema_1177 import Schema1177

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1173_item_data in _users:
            componentsschemas_schema1173_item = Schema1174.from_dict(componentsschemas_schema1173_item_data)

            users.append(componentsschemas_schema1173_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1176_item_data in _teams:
            componentsschemas_schema1176_item = Schema1177.from_dict(componentsschemas_schema1176_item_data)

            teams.append(componentsschemas_schema1176_item)

        skill_collection_shares_response = cls(
            users=users,
            teams=teams,
        )

        return skill_collection_shares_response
