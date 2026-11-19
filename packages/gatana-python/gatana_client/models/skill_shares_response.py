from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1433 import Schema1433
    from ..models.schema_1436 import Schema1436
    from ..models.schema_1438 import Schema1438


T = TypeVar("T", bound="SkillSharesResponse")


@_attrs_define
class SkillSharesResponse:
    """
    Attributes:
        users (list[Schema1433]): User accounts with access, oldest share first
        teams (list[Schema1436]): Teams with access, oldest share first; every member of a team has it
        inherited (None | Schema1438): The collection's shares, which apply to this skill as well; null at root
    """

    users: list[Schema1433]
    teams: list[Schema1436]
    inherited: None | Schema1438

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1438 import Schema1438

        users = []
        for componentsschemas_schema1432_item_data in self.users:
            componentsschemas_schema1432_item = componentsschemas_schema1432_item_data.to_dict()
            users.append(componentsschemas_schema1432_item)

        teams = []
        for componentsschemas_schema1435_item_data in self.teams:
            componentsschemas_schema1435_item = componentsschemas_schema1435_item_data.to_dict()
            teams.append(componentsschemas_schema1435_item)

        inherited: dict[str, Any] | None
        if isinstance(self.inherited, Schema1438):
            inherited = self.inherited.to_dict()
        else:
            inherited = self.inherited

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "users": users,
                "teams": teams,
                "inherited": inherited,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1433 import Schema1433
        from ..models.schema_1436 import Schema1436
        from ..models.schema_1438 import Schema1438

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1432_item_data in _users:
            componentsschemas_schema1432_item = Schema1433.from_dict(componentsschemas_schema1432_item_data)

            users.append(componentsschemas_schema1432_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1435_item_data in _teams:
            componentsschemas_schema1435_item = Schema1436.from_dict(componentsschemas_schema1435_item_data)

            teams.append(componentsschemas_schema1435_item)

        def _parse_inherited(data: object) -> None | Schema1438:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1437_type_0 = Schema1438.from_dict(data)

                return componentsschemas_schema1437_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1438, data)

        inherited = _parse_inherited(d.pop("inherited"))

        skill_shares_response = cls(
            users=users,
            teams=teams,
            inherited=inherited,
        )

        return skill_shares_response
