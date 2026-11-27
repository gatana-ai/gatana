from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1506 import Schema1506


T = TypeVar("T", bound="BuiltinSkillDto")


@_attrs_define
class BuiltinSkillDto:
    """
    Attributes:
        uri (str): SKILL.md URI for agents to use through Gatana
        name (str):
        description (str): One-line description of when to use the skill
        files (list[Schema1506]): All skill files, including SKILL.md
    """

    uri: str
    name: str
    description: str
    files: list[Schema1506]

    def to_dict(self) -> dict[str, Any]:
        uri = self.uri

        name = self.name

        description = self.description

        files = []
        for componentsschemas_schema1505_item_data in self.files:
            componentsschemas_schema1505_item = componentsschemas_schema1505_item_data.to_dict()
            files.append(componentsschemas_schema1505_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "uri": uri,
                "name": name,
                "description": description,
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1506 import Schema1506

        d = dict(src_dict)
        uri = d.pop("uri")

        name = d.pop("name")

        description = d.pop("description")

        files = []
        _files = d.pop("files")
        for componentsschemas_schema1505_item_data in _files:
            componentsschemas_schema1505_item = Schema1506.from_dict(componentsschemas_schema1505_item_data)

            files.append(componentsschemas_schema1505_item)

        builtin_skill_dto = cls(
            uri=uri,
            name=name,
            description=description,
            files=files,
        )

        return builtin_skill_dto
