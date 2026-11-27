from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.skill_file_dto import SkillFileDto


T = TypeVar("T", bound="ListSkillFilesResponse")


@_attrs_define
class ListSkillFilesResponse:
    """
    Attributes:
        files (list[SkillFileDto]): Every file of the skill, SKILL.md included
    """

    files: list[SkillFileDto]

    def to_dict(self) -> dict[str, Any]:
        files = []
        for componentsschemas_schema1455_item_data in self.files:
            componentsschemas_schema1455_item = componentsschemas_schema1455_item_data.to_dict()
            files.append(componentsschemas_schema1455_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.skill_file_dto import SkillFileDto

        d = dict(src_dict)
        files = []
        _files = d.pop("files")
        for componentsschemas_schema1455_item_data in _files:
            componentsschemas_schema1455_item = SkillFileDto.from_dict(componentsschemas_schema1455_item_data)

            files.append(componentsschemas_schema1455_item)

        list_skill_files_response = cls(
            files=files,
        )

        return list_skill_files_response
