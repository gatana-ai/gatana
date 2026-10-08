from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.server_tool_dto import ServerToolDto


T = TypeVar("T", bound="Schema607")


@_attrs_define
class Schema607:
    """
    Attributes:
        tools (list[ServerToolDto]):
    """

    tools: list[ServerToolDto]

    def to_dict(self) -> dict[str, Any]:
        tools = []
        for tools_item_data in self.tools:
            tools_item = tools_item_data.to_dict()
            tools.append(tools_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tools": tools,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_tool_dto import ServerToolDto

        d = dict(src_dict)
        tools = []
        _tools = d.pop("tools")
        for tools_item_data in _tools:
            tools_item = ServerToolDto.from_dict(tools_item_data)

            tools.append(tools_item)

        schema_607 = cls(
            tools=tools,
        )

        return schema_607
