from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.skill_collection_dto import SkillCollectionDto
    from ..models.skill_dto import SkillDto


T = TypeVar("T", bound="ListSkillsResponse")


@_attrs_define
class ListSkillsResponse:
    """
    Attributes:
        skills (list[SkillDto]):
        collections (list[SkillCollectionDto]): The collections the caller can see, whether or not a listed skill is in
            them
    """

    skills: list[SkillDto]
    collections: list[SkillCollectionDto]

    def to_dict(self) -> dict[str, Any]:
        skills = []
        for componentsschemas_schema1151_item_data in self.skills:
            componentsschemas_schema1151_item = componentsschemas_schema1151_item_data.to_dict()
            skills.append(componentsschemas_schema1151_item)

        collections = []
        for componentsschemas_schema1152_item_data in self.collections:
            componentsschemas_schema1152_item = componentsschemas_schema1152_item_data.to_dict()
            collections.append(componentsschemas_schema1152_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "skills": skills,
                "collections": collections,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.skill_collection_dto import SkillCollectionDto
        from ..models.skill_dto import SkillDto

        d = dict(src_dict)
        skills = []
        _skills = d.pop("skills")
        for componentsschemas_schema1151_item_data in _skills:
            componentsschemas_schema1151_item = SkillDto.from_dict(componentsschemas_schema1151_item_data)

            skills.append(componentsschemas_schema1151_item)

        collections = []
        _collections = d.pop("collections")
        for componentsschemas_schema1152_item_data in _collections:
            componentsschemas_schema1152_item = SkillCollectionDto.from_dict(componentsschemas_schema1152_item_data)

            collections.append(componentsschemas_schema1152_item)

        list_skills_response = cls(
            skills=skills,
            collections=collections,
        )

        return list_skills_response
