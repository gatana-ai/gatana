from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1193 import Schema1193
    from ..models.schema_1198 import Schema1198


T = TypeVar("T", bound="ProfileAssignmentsResponse")


@_attrs_define
class ProfileAssignmentsResponse:
    """
    Attributes:
        accounts (list[Schema1193]): Users directly assigned to the profile
        teams (list[Schema1198]): Teams assigned to the profile
    """

    accounts: list[Schema1193]
    teams: list[Schema1198]

    def to_dict(self) -> dict[str, Any]:
        accounts = []
        for componentsschemas_schema1192_item_data in self.accounts:
            componentsschemas_schema1192_item = componentsschemas_schema1192_item_data.to_dict()
            accounts.append(componentsschemas_schema1192_item)

        teams = []
        for componentsschemas_schema1197_item_data in self.teams:
            componentsschemas_schema1197_item = componentsschemas_schema1197_item_data.to_dict()
            teams.append(componentsschemas_schema1197_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "accounts": accounts,
                "teams": teams,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1193 import Schema1193
        from ..models.schema_1198 import Schema1198

        d = dict(src_dict)
        accounts = []
        _accounts = d.pop("accounts")
        for componentsschemas_schema1192_item_data in _accounts:
            componentsschemas_schema1192_item = Schema1193.from_dict(componentsschemas_schema1192_item_data)

            accounts.append(componentsschemas_schema1192_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1197_item_data in _teams:
            componentsschemas_schema1197_item = Schema1198.from_dict(componentsschemas_schema1197_item_data)

            teams.append(componentsschemas_schema1197_item)

        profile_assignments_response = cls(
            accounts=accounts,
            teams=teams,
        )

        return profile_assignments_response
