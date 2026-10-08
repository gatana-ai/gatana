from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.call_mcp_server_tool_body_args import CallMcpServerToolBodyArgs


T = TypeVar("T", bound="CallMcpServerToolBody")


@_attrs_define
class CallMcpServerToolBody:
    """
    Attributes:
        args (CallMcpServerToolBodyArgs):
    """

    args: CallMcpServerToolBodyArgs
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        args = self.args.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "args": args,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.call_mcp_server_tool_body_args import CallMcpServerToolBodyArgs

        d = dict(src_dict)
        args = CallMcpServerToolBodyArgs.from_dict(d.pop("args"))

        call_mcp_server_tool_body = cls(
            args=args,
        )

        call_mcp_server_tool_body.additional_properties = d
        return call_mcp_server_tool_body

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
