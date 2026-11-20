from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1371 import Schema1371
    from ..models.schema_1373 import Schema1373


T = TypeVar("T", bound="ArtifactSharesResponse")


@_attrs_define
class ArtifactSharesResponse:
    """
    Attributes:
        users (list[Schema1371]): User accounts the artifact is shared with, oldest share first
        teams (list[Schema1373]): Teams the artifact is shared with, oldest share first; every member of a team can open
            it
    """

    users: list[Schema1371]
    teams: list[Schema1373]

    def to_dict(self) -> dict[str, Any]:
        users = []
        for componentsschemas_schema1370_item_data in self.users:
            componentsschemas_schema1370_item = componentsschemas_schema1370_item_data.to_dict()
            users.append(componentsschemas_schema1370_item)

        teams = []
        for componentsschemas_schema1372_item_data in self.teams:
            componentsschemas_schema1372_item = componentsschemas_schema1372_item_data.to_dict()
            teams.append(componentsschemas_schema1372_item)

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
        from ..models.schema_1371 import Schema1371
        from ..models.schema_1373 import Schema1373

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1370_item_data in _users:
            componentsschemas_schema1370_item = Schema1371.from_dict(componentsschemas_schema1370_item_data)

            users.append(componentsschemas_schema1370_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1372_item_data in _teams:
            componentsschemas_schema1372_item = Schema1373.from_dict(componentsschemas_schema1372_item_data)

            teams.append(componentsschemas_schema1372_item)

        artifact_shares_response = cls(
            users=users,
            teams=teams,
        )

        return artifact_shares_response
