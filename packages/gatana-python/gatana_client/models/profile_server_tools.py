from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.profile_tool_entry import ProfileToolEntry


T = TypeVar("T", bound="ProfileServerTools")


@_attrs_define
class ProfileServerTools:
    """
    Attributes:
        server_slug (str): Slug of the MCP server that the configuration applies to
        are_all_tools_enabled (bool): Whether every tool of the server is available to the profile
        auto_enable_new_tools (bool): Whether tools that the server adds later become available to the profile
            automatically
        tools (list[ProfileToolEntry]): Per-tool configuration of the profile for the server
    """

    server_slug: str
    are_all_tools_enabled: bool
    auto_enable_new_tools: bool
    tools: list[ProfileToolEntry]

    def to_dict(self) -> dict[str, Any]:
        server_slug = self.server_slug

        are_all_tools_enabled = self.are_all_tools_enabled

        auto_enable_new_tools = self.auto_enable_new_tools

        tools = []
        for componentsschemas_schema1031_item_data in self.tools:
            componentsschemas_schema1031_item = componentsschemas_schema1031_item_data.to_dict()
            tools.append(componentsschemas_schema1031_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "serverSlug": server_slug,
                "areAllToolsEnabled": are_all_tools_enabled,
                "autoEnableNewTools": auto_enable_new_tools,
                "tools": tools,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_tool_entry import ProfileToolEntry

        d = dict(src_dict)
        server_slug = d.pop("serverSlug")

        are_all_tools_enabled = d.pop("areAllToolsEnabled")

        auto_enable_new_tools = d.pop("autoEnableNewTools")

        tools = []
        _tools = d.pop("tools")
        for componentsschemas_schema1031_item_data in _tools:
            componentsschemas_schema1031_item = ProfileToolEntry.from_dict(componentsschemas_schema1031_item_data)

            tools.append(componentsschemas_schema1031_item)

        profile_server_tools = cls(
            server_slug=server_slug,
            are_all_tools_enabled=are_all_tools_enabled,
            auto_enable_new_tools=auto_enable_new_tools,
            tools=tools,
        )

        return profile_server_tools
