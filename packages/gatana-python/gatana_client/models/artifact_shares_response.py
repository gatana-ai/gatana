from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1198 import Schema1198
    from ..models.schema_1200 import Schema1200


T = TypeVar("T", bound="ArtifactSharesResponse")


@_attrs_define
class ArtifactSharesResponse:
    """
    Attributes:
        users (list[Schema1198]): User accounts the artifact is shared with, oldest share first
        teams (list[Schema1200]): Teams the artifact is shared with, oldest share first; every member of a team can open
            it
    """

    users: list[Schema1198]
    teams: list[Schema1200]

    def to_dict(self) -> dict[str, Any]:
        users = []
        for componentsschemas_schema1197_item_data in self.users:
            componentsschemas_schema1197_item = componentsschemas_schema1197_item_data.to_dict()
            users.append(componentsschemas_schema1197_item)

        teams = []
        for componentsschemas_schema1199_item_data in self.teams:
            componentsschemas_schema1199_item = componentsschemas_schema1199_item_data.to_dict()
            teams.append(componentsschemas_schema1199_item)

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
        from ..models.schema_1198 import Schema1198
        from ..models.schema_1200 import Schema1200

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1197_item_data in _users:
            componentsschemas_schema1197_item = Schema1198.from_dict(componentsschemas_schema1197_item_data)

            users.append(componentsschemas_schema1197_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1199_item_data in _teams:
            componentsschemas_schema1199_item = Schema1200.from_dict(componentsschemas_schema1199_item_data)

            teams.append(componentsschemas_schema1199_item)

        artifact_shares_response = cls(
            users=users,
            teams=teams,
        )

        return artifact_shares_response
