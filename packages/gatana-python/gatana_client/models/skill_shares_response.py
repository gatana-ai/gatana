from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1466 import Schema1466
    from ..models.schema_1469 import Schema1469
    from ..models.schema_1471 import Schema1471
    from ..models.schema_1473 import Schema1473


T = TypeVar("T", bound="SkillSharesResponse")


@_attrs_define
class SkillSharesResponse:
    """
    Attributes:
        users (list[Schema1466]): User accounts with access, oldest share first
        teams (list[Schema1469]): Teams with access, oldest share first; every member of a team has it
        servers (list[Schema1471]): Servers in order of attachment, oldest first. Server access grants read access to
            the skill
        inherited (None | Schema1473): The collection's shares, which apply to this skill as well; null at root
    """

    users: list[Schema1466]
    teams: list[Schema1469]
    servers: list[Schema1471]
    inherited: None | Schema1473

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1473 import Schema1473

        users = []
        for componentsschemas_schema1465_item_data in self.users:
            componentsschemas_schema1465_item = componentsschemas_schema1465_item_data.to_dict()
            users.append(componentsschemas_schema1465_item)

        teams = []
        for componentsschemas_schema1468_item_data in self.teams:
            componentsschemas_schema1468_item = componentsschemas_schema1468_item_data.to_dict()
            teams.append(componentsschemas_schema1468_item)

        servers = []
        for componentsschemas_schema1470_item_data in self.servers:
            componentsschemas_schema1470_item = componentsschemas_schema1470_item_data.to_dict()
            servers.append(componentsschemas_schema1470_item)

        inherited: dict[str, Any] | None
        if isinstance(self.inherited, Schema1473):
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
        from ..models.schema_1466 import Schema1466
        from ..models.schema_1469 import Schema1469
        from ..models.schema_1471 import Schema1471
        from ..models.schema_1473 import Schema1473

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for componentsschemas_schema1465_item_data in _users:
            componentsschemas_schema1465_item = Schema1466.from_dict(componentsschemas_schema1465_item_data)

            users.append(componentsschemas_schema1465_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1468_item_data in _teams:
            componentsschemas_schema1468_item = Schema1469.from_dict(componentsschemas_schema1468_item_data)

            teams.append(componentsschemas_schema1468_item)

        servers = []
        _servers = d.pop("servers")
        for componentsschemas_schema1470_item_data in _servers:
            componentsschemas_schema1470_item = Schema1471.from_dict(componentsschemas_schema1470_item_data)

            servers.append(componentsschemas_schema1470_item)

        def _parse_inherited(data: object) -> None | Schema1473:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1472_type_0 = Schema1473.from_dict(data)

                return componentsschemas_schema1472_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1473, data)

        inherited = _parse_inherited(d.pop("inherited"))

        skill_shares_response = cls(
            users=users,
            teams=teams,
            servers=servers,
            inherited=inherited,
        )

        return skill_shares_response
