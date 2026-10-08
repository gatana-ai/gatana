from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.call_mcp_server_tool_response_200_result import CallMcpServerToolResponse200Result


T = TypeVar("T", bound="CallMcpServerToolResponse200")


@_attrs_define
class CallMcpServerToolResponse200:
    """
    Attributes:
        result (CallMcpServerToolResponse200Result | Unset):
    """

    result: CallMcpServerToolResponse200Result | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.call_mcp_server_tool_response_200_result import CallMcpServerToolResponse200Result

        d = dict(src_dict)
        _result = d.pop("result", UNSET)
        result: CallMcpServerToolResponse200Result | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = CallMcpServerToolResponse200Result.from_dict(_result)

        call_mcp_server_tool_response_200 = cls(
            result=result,
        )

        return call_mcp_server_tool_response_200
