from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1487 import Schema1487
    from ..models.server_skill_dto import ServerSkillDto


T = TypeVar("T", bound="ListServerSkillsResponse")


@_attrs_define
class ListServerSkillsResponse:
    """
    Attributes:
        skills (list[ServerSkillDto]):
        servers (list[Schema1487]): The servers of the listed skills
    """

    skills: list[ServerSkillDto]
    servers: list[Schema1487]

    def to_dict(self) -> dict[str, Any]:
        skills = []
        for componentsschemas_schema1475_item_data in self.skills:
            componentsschemas_schema1475_item = componentsschemas_schema1475_item_data.to_dict()
            skills.append(componentsschemas_schema1475_item)

        servers = []
        for componentsschemas_schema1486_item_data in self.servers:
            componentsschemas_schema1486_item = componentsschemas_schema1486_item_data.to_dict()
            servers.append(componentsschemas_schema1486_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "skills": skills,
                "servers": servers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1487 import Schema1487
        from ..models.server_skill_dto import ServerSkillDto

        d = dict(src_dict)
        skills = []
        _skills = d.pop("skills")
        for componentsschemas_schema1475_item_data in _skills:
            componentsschemas_schema1475_item = ServerSkillDto.from_dict(componentsschemas_schema1475_item_data)

            skills.append(componentsschemas_schema1475_item)

        servers = []
        _servers = d.pop("servers")
        for componentsschemas_schema1486_item_data in _servers:
            componentsschemas_schema1486_item = Schema1487.from_dict(componentsschemas_schema1486_item_data)

            servers.append(componentsschemas_schema1486_item)

        list_server_skills_response = cls(
            skills=skills,
            servers=servers,
        )

        return list_server_skills_response
