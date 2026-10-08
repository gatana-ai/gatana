from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema627")


@_attrs_define
class Schema627:
    """
    Attributes:
        tool_name (str): Tool name as reported by the MCP server
        tool_name_override (str): Replacement tool name, applied when overrideToolName is true
        description (str): Tool description as reported by the MCP server
        description_override (str): Replacement description, applied when overrideDescription is true
        server_slug (str):
        is_enabled (bool): Whether the tool is enabled and exposed to clients
    """

    tool_name: str
    tool_name_override: str
    description: str
    description_override: str
    server_slug: str
    is_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        tool_name = self.tool_name

        tool_name_override = self.tool_name_override

        description = self.description

        description_override = self.description_override

        server_slug = self.server_slug

        is_enabled = self.is_enabled

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "toolName": tool_name,
                "toolNameOverride": tool_name_override,
                "description": description,
                "descriptionOverride": description_override,
                "serverSlug": server_slug,
                "isEnabled": is_enabled,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tool_name = d.pop("toolName")

        tool_name_override = d.pop("toolNameOverride")

        description = d.pop("description")

        description_override = d.pop("descriptionOverride")

        server_slug = d.pop("serverSlug")

        is_enabled = d.pop("isEnabled")

        schema_627 = cls(
            tool_name=tool_name,
            tool_name_override=tool_name_override,
            description=description,
            description_override=description_override,
            server_slug=server_slug,
            is_enabled=is_enabled,
        )

        return schema_627
