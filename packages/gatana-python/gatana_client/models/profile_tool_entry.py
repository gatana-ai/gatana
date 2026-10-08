from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ProfileToolEntry")


@_attrs_define
class ProfileToolEntry:
    """
    Attributes:
        tool_name (str): Name of the tool as the MCP server itself reports it
        is_promoted (bool): Whether the tool stays listed while the session runs in code mode
        tool_name_override (str): Name that the tool is exposed under to MCP clients, without the server-slug prefix;
            empty when the tool keeps its regular name
    """

    tool_name: str
    is_promoted: bool
    tool_name_override: str

    def to_dict(self) -> dict[str, Any]:
        tool_name = self.tool_name

        is_promoted = self.is_promoted

        tool_name_override = self.tool_name_override

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "toolName": tool_name,
                "isPromoted": is_promoted,
                "toolNameOverride": tool_name_override,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tool_name = d.pop("toolName")

        is_promoted = d.pop("isPromoted")

        tool_name_override = d.pop("toolNameOverride")

        profile_tool_entry = cls(
            tool_name=tool_name,
            is_promoted=is_promoted,
            tool_name_override=tool_name_override,
        )

        return profile_tool_entry
