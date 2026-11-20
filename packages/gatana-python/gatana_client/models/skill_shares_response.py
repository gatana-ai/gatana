from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1456 import Schema1456
    from ..models.schema_1459 import Schema1459
    from ..models.schema_1461 import Schema1461
    from ..models.schema_1463 import Schema1463


T = TypeVar("T", bound="SkillSharesResponse")


@_attrs_define
class SkillSharesResponse:
    """
    Attributes:
        users (list[Schema1456]): User accounts with access, oldest share first
        teams (list[Schema1459]): Teams with access, oldest share first; every member of a team has it
        servers (list[Schema1461]): Servers in order of attachment, oldest first. Server access grants read access to
            the skill
        inherited (None | Schema1463): The collection's shares, which apply to this skill as well; null at root
    """

    users: list[Schema1456]
    teams: list[Schema1459]
    servers: list[Schema1461]
    inherited: None | Schema1463

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1463 import Schema1463

        users = []
        for componentsschemas_schema1455_item_data in self.users:
            componentsschemas_schema1455_item = componentsschemas_schema1455_item_data.to_dict()
            users.append(componentsschemas_schema1455_item)

        teams = []
        for componentsschemas_schema1458_item_data in self.teams:
            componentsschemas_schema1458_item = componentsschemas_schema1458_item_data.to_dict()
            teams.append(componentsschemas_schema1458_item)

        servers = []
        for componentsschemas_schema1460_item_data in self.servers:
            componentsschemas_schema1460_item = componentsschemas_schema1460_item_data.to_dict()
            servers.append(componentsschemas_schema1460_item)

        inherited: dict[str, Any] | None
        if isinstance(self.inherited, Schema1463):
            inherited = self.inherited.to_dict()
        else:
            inherited = self.inherited

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "users": users,
                "teams": teams,
                "servers": servers,
                "inherited": inherited,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1456 import Schema1456
        from ..models.schema_1459 import Schema1459
        from ..models.schema_1461 import Schema1461
        from ..models.schema_1463 import Schema1463

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1455_item_data in _users:
            componentsschemas_schema1455_item = Schema1456.from_dict(componentsschemas_schema1455_item_data)

            users.append(componentsschemas_schema1455_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1458_item_data in _teams:
            componentsschemas_schema1458_item = Schema1459.from_dict(componentsschemas_schema1458_item_data)

            teams.append(componentsschemas_schema1458_item)

        servers = []
        _servers = d.pop("servers")
        for componentsschemas_schema1460_item_data in _servers:
            componentsschemas_schema1460_item = Schema1461.from_dict(componentsschemas_schema1460_item_data)

            servers.append(componentsschemas_schema1460_item)

        def _parse_inherited(data: object) -> None | Schema1463:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1462_type_0 = Schema1463.from_dict(data)

                return componentsschemas_schema1462_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1463, data)

        inherited = _parse_inherited(d.pop("inherited"))

        skill_shares_response = cls(
            users=users,
            teams=teams,
            servers=servers,
            inherited=inherited,
        )

        return skill_shares_response
