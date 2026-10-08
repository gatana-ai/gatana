from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1174 import Schema1174
    from ..models.schema_1177 import Schema1177
    from ..models.schema_1179 import Schema1179


T = TypeVar("T", bound="SkillSharesResponse")


@_attrs_define
class SkillSharesResponse:
    """
    Attributes:
        users (list[Schema1174]): User accounts with access, oldest share first
        teams (list[Schema1177]): Teams with access, oldest share first; every member of a team has it
        inherited (None | Schema1179): The collection's shares, which apply to this skill as well; null at root
    """

    users: list[Schema1174]
    teams: list[Schema1177]
    inherited: None | Schema1179

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1179 import Schema1179

        users = []
        for componentsschemas_schema1173_item_data in self.users:
            componentsschemas_schema1173_item = componentsschemas_schema1173_item_data.to_dict()
            users.append(componentsschemas_schema1173_item)

        teams = []
        for componentsschemas_schema1176_item_data in self.teams:
            componentsschemas_schema1176_item = componentsschemas_schema1176_item_data.to_dict()
            teams.append(componentsschemas_schema1176_item)

        inherited: dict[str, Any] | None
        if isinstance(self.inherited, Schema1179):
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
        from ..models.schema_1174 import Schema1174
        from ..models.schema_1177 import Schema1177
        from ..models.schema_1179 import Schema1179

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1173_item_data in _users:
            componentsschemas_schema1173_item = Schema1174.from_dict(componentsschemas_schema1173_item_data)

            users.append(componentsschemas_schema1173_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1176_item_data in _teams:
            componentsschemas_schema1176_item = Schema1177.from_dict(componentsschemas_schema1176_item_data)

            teams.append(componentsschemas_schema1176_item)

        def _parse_inherited(data: object) -> None | Schema1179:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1178_type_0 = Schema1179.from_dict(data)

                return componentsschemas_schema1178_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1179, data)

        inherited = _parse_inherited(d.pop("inherited"))

        skill_shares_response = cls(
            users=users,
            teams=teams,
            inherited=inherited,
        )

        return skill_shares_response
