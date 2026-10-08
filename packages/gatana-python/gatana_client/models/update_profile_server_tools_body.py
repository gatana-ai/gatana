from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schema_270 import Schema270


T = TypeVar("T", bound="UpdateProfileServerToolsBody")


@_attrs_define
class UpdateProfileServerToolsBody:
    """
    Attributes:
        are_all_tools_enabled (bool): Whether every tool of the server is available to the profile
        auto_enable_new_tools (bool): Whether tools that the server adds later become available to the profile
            automatically
        tools (list[Schema270]): Tools of the server that the profile enables, promotes or renames
    """

    are_all_tools_enabled: bool
    auto_enable_new_tools: bool
    tools: list[Schema270]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        are_all_tools_enabled = self.are_all_tools_enabled

        auto_enable_new_tools = self.auto_enable_new_tools

        tools = []
        for tools_item_data in self.tools:
            tools_item = tools_item_data.to_dict()
            tools.append(tools_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "areAllToolsEnabled": are_all_tools_enabled,
                "autoEnableNewTools": auto_enable_new_tools,
                "tools": tools,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_270 import Schema270

        d = dict(src_dict)
        are_all_tools_enabled = d.pop("areAllToolsEnabled")

        auto_enable_new_tools = d.pop("autoEnableNewTools")

        tools = []
        _tools = d.pop("tools")
        for tools_item_data in _tools:
            tools_item = Schema270.from_dict(tools_item_data)

            tools.append(tools_item)

        update_profile_server_tools_body = cls(
            are_all_tools_enabled=are_all_tools_enabled,
            auto_enable_new_tools=auto_enable_new_tools,
            tools=tools,
        )

        update_profile_server_tools_body.additional_properties = d
        return update_profile_server_tools_body

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
