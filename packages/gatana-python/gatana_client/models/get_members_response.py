from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_680_item import Schema680Item
    from ..models.schema_681_item import Schema681Item


T = TypeVar("T", bound="GetMembersResponse")


@_attrs_define
class GetMembersResponse:
    """
    Attributes:
        teams (list[Schema680Item]):
        users (list[Schema681Item]):
    """

    teams: list[Schema680Item]
    users: list[Schema681Item]

    def to_dict(self) -> dict[str, Any]:
        teams = []
        for componentsschemas_schema680_item_data in self.teams:
            componentsschemas_schema680_item = componentsschemas_schema680_item_data.to_dict()
            teams.append(componentsschemas_schema680_item)

        users = []
        for componentsschemas_schema681_item_data in self.users:
            componentsschemas_schema681_item = componentsschemas_schema681_item_data.to_dict()
            users.append(componentsschemas_schema681_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "teams": teams,
                "users": users,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_680_item import Schema680Item
        from ..models.schema_681_item import Schema681Item

        d = dict(src_dict)
        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema680_item_data in _teams:
            componentsschemas_schema680_item = Schema680Item.from_dict(componentsschemas_schema680_item_data)

            teams.append(componentsschemas_schema680_item)

        users = []
        _users = d.pop("users")
        for componentsschemas_schema681_item_data in _users:
            componentsschemas_schema681_item = Schema681Item.from_dict(componentsschemas_schema681_item_data)

            users.append(componentsschemas_schema681_item)

        get_members_response = cls(
            teams=teams,
            users=users,
        )

        return get_members_response
