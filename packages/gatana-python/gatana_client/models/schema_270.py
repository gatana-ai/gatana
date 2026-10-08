from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Schema270")


@_attrs_define
class Schema270:
    """
    Attributes:
        tool_name (str): Name of the tool as the MCP server itself reports it
        is_promoted (bool): Whether the tool stays listed while the session runs in code mode
        tool_name_override (Literal[''] | str): Name that the tool is exposed under to MCP clients, without the server-
            slug prefix; empty when the tool keeps its regular name
    """

    tool_name: str
    is_promoted: bool
    tool_name_override: Literal[""] | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool_name = self.tool_name

        is_promoted = self.is_promoted

        tool_name_override: Literal[""] | str
        tool_name_override = self.tool_name_override

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
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

        def _parse_tool_name_override(data: object) -> Literal[""] | str:
            tool_name_override_type_0 = cast(Literal[""], data)
            if tool_name_override_type_0 != "":
                raise ValueError(f"toolNameOverride_type_0 must match const '', got '{tool_name_override_type_0}'")
            return tool_name_override_type_0
            return cast(Literal[""] | str, data)

        tool_name_override = _parse_tool_name_override(d.pop("toolNameOverride"))

        schema_270 = cls(
            tool_name=tool_name,
            is_promoted=is_promoted,
            tool_name_override=tool_name_override,
        )

        schema_270.additional_properties = d
        return schema_270

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
