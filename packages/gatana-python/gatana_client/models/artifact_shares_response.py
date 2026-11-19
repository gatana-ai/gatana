from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1350 import Schema1350
    from ..models.schema_1352 import Schema1352


T = TypeVar("T", bound="ArtifactSharesResponse")


@_attrs_define
class ArtifactSharesResponse:
    """
    Attributes:
        users (list[Schema1350]): User accounts the artifact is shared with, oldest share first
        teams (list[Schema1352]): Teams the artifact is shared with, oldest share first; every member of a team can open
            it
    """

    users: list[Schema1350]
    teams: list[Schema1352]

    def to_dict(self) -> dict[str, Any]:
        users = []
        for componentsschemas_schema1349_item_data in self.users:
            componentsschemas_schema1349_item = componentsschemas_schema1349_item_data.to_dict()
            users.append(componentsschemas_schema1349_item)

        teams = []
        for componentsschemas_schema1351_item_data in self.teams:
            componentsschemas_schema1351_item = componentsschemas_schema1351_item_data.to_dict()
            teams.append(componentsschemas_schema1351_item)

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
        from ..models.schema_1350 import Schema1350
        from ..models.schema_1352 import Schema1352

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1349_item_data in _users:
            componentsschemas_schema1349_item = Schema1350.from_dict(componentsschemas_schema1349_item_data)

            users.append(componentsschemas_schema1349_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1351_item_data in _teams:
            componentsschemas_schema1351_item = Schema1352.from_dict(componentsschemas_schema1351_item_data)

            teams.append(componentsschemas_schema1351_item)

        artifact_shares_response = cls(
            users=users,
            teams=teams,
        )

        return artifact_shares_response
