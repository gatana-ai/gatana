from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_773_item import Schema773Item
    from ..models.schema_774_item import Schema774Item


T = TypeVar("T", bound="GetMembersResponse")


@_attrs_define
class GetMembersResponse:
    """
    Attributes:
        teams (list[Schema773Item]):
        users (list[Schema774Item]):
    """

    teams: list[Schema773Item]
    users: list[Schema774Item]

    def to_dict(self) -> dict[str, Any]:
        teams = []
        for componentsschemas_schema773_item_data in self.teams:
            componentsschemas_schema773_item = componentsschemas_schema773_item_data.to_dict()
            teams.append(componentsschemas_schema773_item)

        users = []
        for componentsschemas_schema774_item_data in self.users:
            componentsschemas_schema774_item = componentsschemas_schema774_item_data.to_dict()
            users.append(componentsschemas_schema774_item)

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
        from ..models.schema_773_item import Schema773Item
        from ..models.schema_774_item import Schema774Item

        d = dict(src_dict)
        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema773_item_data in _teams:
            componentsschemas_schema773_item = Schema773Item.from_dict(componentsschemas_schema773_item_data)

            teams.append(componentsschemas_schema773_item)

        users = []
        _users = d.pop("users")
        for componentsschemas_schema774_item_data in _users:
            componentsschemas_schema774_item = Schema774Item.from_dict(componentsschemas_schema774_item_data)

            users.append(componentsschemas_schema774_item)

        get_members_response = cls(
            teams=teams,
            users=users,
        )

        return get_members_response
