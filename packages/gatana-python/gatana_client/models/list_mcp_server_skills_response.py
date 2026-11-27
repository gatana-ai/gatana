from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.server_skill_dto import ServerSkillDto


T = TypeVar("T", bound="ListMcpServerSkillsResponse")


@_attrs_define
class ListMcpServerSkillsResponse:
    """
    Attributes:
        skills (list[ServerSkillDto]):
    """

    skills: list[ServerSkillDto]

    def to_dict(self) -> dict[str, Any]:
        skills = []
        for componentsschemas_schema1489_item_data in self.skills:
            componentsschemas_schema1489_item = componentsschemas_schema1489_item_data.to_dict()
            skills.append(componentsschemas_schema1489_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "skills": skills,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_skill_dto import ServerSkillDto

        d = dict(src_dict)
        skills = []
        _skills = d.pop("skills")
        for componentsschemas_schema1489_item_data in _skills:
            componentsschemas_schema1489_item = ServerSkillDto.from_dict(componentsschemas_schema1489_item_data)

            skills.append(componentsschemas_schema1489_item)

        list_mcp_server_skills_response = cls(
            skills=skills,
        )

        return list_mcp_server_skills_response
