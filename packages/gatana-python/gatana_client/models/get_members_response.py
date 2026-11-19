from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_825_item import Schema825Item
    from ..models.schema_826_item import Schema826Item


T = TypeVar("T", bound="GetMembersResponse")


@_attrs_define
class GetMembersResponse:
    """
    Attributes:
        teams (list[Schema825Item]):
        users (list[Schema826Item]):
    """

    teams: list[Schema825Item]
    users: list[Schema826Item]

    def to_dict(self) -> dict[str, Any]:
        teams = []
        for componentsschemas_schema825_item_data in self.teams:
            componentsschemas_schema825_item = componentsschemas_schema825_item_data.to_dict()
            teams.append(componentsschemas_schema825_item)

        users = []
        for componentsschemas_schema826_item_data in self.users:
            componentsschemas_schema826_item = componentsschemas_schema826_item_data.to_dict()
            users.append(componentsschemas_schema826_item)

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
        from ..models.schema_825_item import Schema825Item
        from ..models.schema_826_item import Schema826Item

        d = dict(src_dict)
        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema825_item_data in _teams:
            componentsschemas_schema825_item = Schema825Item.from_dict(componentsschemas_schema825_item_data)

            teams.append(componentsschemas_schema825_item)

        users = []
        _users = d.pop("users")
        for componentsschemas_schema826_item_data in _users:
            componentsschemas_schema826_item = Schema826Item.from_dict(componentsschemas_schema826_item_data)

            users.append(componentsschemas_schema826_item)

        get_members_response = cls(
            teams=teams,
            users=users,
        )

        return get_members_response
