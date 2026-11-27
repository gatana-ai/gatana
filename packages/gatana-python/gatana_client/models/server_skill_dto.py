from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1483 import Schema1483


T = TypeVar("T", bound="ServerSkillDto")


@_attrs_define
class ServerSkillDto:
    """
    Attributes:
        server_id (str):
        server_slug (str):
        uri (str): URI of the SKILL.md as the server publishes it
        gateway_uri (str): URI of the SKILL.md as agents read it through Gatana
        name (str):
        description (str): One line saying when to use the skill
        files (list[Schema1483]): Every file of the skill, SKILL.md included
    """

    server_id: str
    server_slug: str
    uri: str
    gateway_uri: str
    name: str
    description: str
    files: list[Schema1483]

    def to_dict(self) -> dict[str, Any]:
        server_id = self.server_id

        server_slug = self.server_slug

        uri = self.uri

        gateway_uri = self.gateway_uri

        name = self.name

        description = self.description

        files = []
        for componentsschemas_schema1482_item_data in self.files:
            componentsschemas_schema1482_item = componentsschemas_schema1482_item_data.to_dict()
            files.append(componentsschemas_schema1482_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "serverId": server_id,
                "serverSlug": server_slug,
                "uri": uri,
                "gatewayUri": gateway_uri,
                "name": name,
                "description": description,
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1483 import Schema1483

        d = dict(src_dict)
        server_id = d.pop("serverId")

        server_slug = d.pop("serverSlug")

        uri = d.pop("uri")

        gateway_uri = d.pop("gatewayUri")

        name = d.pop("name")

        description = d.pop("description")

        files = []
        _files = d.pop("files")
        for componentsschemas_schema1482_item_data in _files:
            componentsschemas_schema1482_item = Schema1483.from_dict(componentsschemas_schema1482_item_data)

            files.append(componentsschemas_schema1482_item)

        server_skill_dto = cls(
            server_id=server_id,
            server_slug=server_slug,
            uri=uri,
            gateway_uri=gateway_uri,
            name=name,
            description=description,
            files=files,
        )

        return server_skill_dto
