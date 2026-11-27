from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1381 import Schema1381
    from ..models.schema_1383 import Schema1383


T = TypeVar("T", bound="ArtifactSharesResponse")


@_attrs_define
class ArtifactSharesResponse:
    """
    Attributes:
        users (list[Schema1381]): User accounts the artifact is shared with, oldest share first
        teams (list[Schema1383]): Teams the artifact is shared with, oldest share first; every member of a team can open
            it
    """

    users: list[Schema1381]
    teams: list[Schema1383]

    def to_dict(self) -> dict[str, Any]:
        users = []
        for componentsschemas_schema1380_item_data in self.users:
            componentsschemas_schema1380_item = componentsschemas_schema1380_item_data.to_dict()
            users.append(componentsschemas_schema1380_item)

        teams = []
        for componentsschemas_schema1382_item_data in self.teams:
            componentsschemas_schema1382_item = componentsschemas_schema1382_item_data.to_dict()
            teams.append(componentsschemas_schema1382_item)

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
        from ..models.schema_1381 import Schema1381
        from ..models.schema_1383 import Schema1383

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1380_item_data in _users:
            componentsschemas_schema1380_item = Schema1381.from_dict(componentsschemas_schema1380_item_data)

            users.append(componentsschemas_schema1380_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1382_item_data in _teams:
            componentsschemas_schema1382_item = Schema1383.from_dict(componentsschemas_schema1382_item_data)

            teams.append(componentsschemas_schema1382_item)

        artifact_shares_response = cls(
            users=users,
            teams=teams,
        )

        return artifact_shares_response
