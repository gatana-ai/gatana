from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.skill_file_dto import SkillFileDto


T = TypeVar("T", bound="ReplaceSkillFilesResponse")


@_attrs_define
class ReplaceSkillFilesResponse:
    """
    Attributes:
        files (list[SkillFileDto]): Every file of the skill after the write, SKILL.md included
        updated_at (str): updatedAt of the skill as this write left it. Equal to the earlier value when the set changed
            nothing
    """

    files: list[SkillFileDto]
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        files = []
        for componentsschemas_schema1427_item_data in self.files:
            componentsschemas_schema1427_item = componentsschemas_schema1427_item_data.to_dict()
            files.append(componentsschemas_schema1427_item)

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "files": files,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.skill_file_dto import SkillFileDto

        d = dict(src_dict)
        files = []
        _files = d.pop("files")
        for componentsschemas_schema1427_item_data in _files:
            componentsschemas_schema1427_item = SkillFileDto.from_dict(componentsschemas_schema1427_item_data)

            files.append(componentsschemas_schema1427_item)

        updated_at = d.pop("updatedAt")

        replace_skill_files_response = cls(
            files=files,
            updated_at=updated_at,
        )

        return replace_skill_files_response
