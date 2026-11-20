from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schema_439 import Schema439


T = TypeVar("T", bound="ReplaceSkillFilesBody")


@_attrs_define
class ReplaceSkillFilesBody:
    """
    Attributes:
        files (list[Schema439]): Replace all files: maximum 512 files and 4 MiB, including SKILL.md. Delete stored files
            omitted from the set. Keep the stored SKILL.md if omitted
    """

    files: list[Schema439]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = []
        for componentsschemas_schema438_item_data in self.files:
            componentsschemas_schema438_item = componentsschemas_schema438_item_data.to_dict()
            files.append(componentsschemas_schema438_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_439 import Schema439

        d = dict(src_dict)
        files = []
        _files = d.pop("files")
        for componentsschemas_schema438_item_data in _files:
            componentsschemas_schema438_item = Schema439.from_dict(componentsschemas_schema438_item_data)

            files.append(componentsschemas_schema438_item)

        replace_skill_files_body = cls(
            files=files,
        )

        replace_skill_files_body.additional_properties = d
        return replace_skill_files_body

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
