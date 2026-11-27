from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1466 import Schema1466
    from ..models.schema_1469 import Schema1469


T = TypeVar("T", bound="SkillCollectionSharesResponse")


@_attrs_define
class SkillCollectionSharesResponse:
    """
    Attributes:
        users (list[Schema1466]): User accounts with access, oldest share first
        teams (list[Schema1469]): Teams with access, oldest share first; every member of a team has it
    """

    users: list[Schema1466]
    teams: list[Schema1469]

    def to_dict(self) -> dict[str, Any]:
        users = []
        for componentsschemas_schema1465_item_data in self.users:
            componentsschemas_schema1465_item = componentsschemas_schema1465_item_data.to_dict()
            users.append(componentsschemas_schema1465_item)

        teams = []
        for componentsschemas_schema1468_item_data in self.teams:
            componentsschemas_schema1468_item = componentsschemas_schema1468_item_data.to_dict()
            teams.append(componentsschemas_schema1468_item)

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
        from ..models.schema_1466 import Schema1466
        from ..models.schema_1469 import Schema1469

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1465_item_data in _users:
            componentsschemas_schema1465_item = Schema1466.from_dict(componentsschemas_schema1465_item_data)

            users.append(componentsschemas_schema1465_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1468_item_data in _teams:
            componentsschemas_schema1468_item = Schema1469.from_dict(componentsschemas_schema1468_item_data)

            teams.append(componentsschemas_schema1468_item)

        skill_collection_shares_response = cls(
            users=users,
            teams=teams,
        )

        return skill_collection_shares_response
