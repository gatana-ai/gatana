from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.call_mcp_server_tool_response_200_result_content_item import (
        CallMcpServerToolResponse200ResultContentItem,
    )
    from ..models.call_mcp_server_tool_response_200_result_structured_content import (
        CallMcpServerToolResponse200ResultStructuredContent,
    )


T = TypeVar("T", bound="CallMcpServerToolResponse200Result")


@_attrs_define
class CallMcpServerToolResponse200Result:
    """
    Attributes:
        is_error (bool | Unset):
        error_code (str | Unset):
        error_message (str | Unset):
        structured_content (CallMcpServerToolResponse200ResultStructuredContent | Unset):
        content (list[CallMcpServerToolResponse200ResultContentItem] | Unset):
    """

    is_error: bool | Unset = UNSET
    error_code: str | Unset = UNSET
    error_message: str | Unset = UNSET
    structured_content: CallMcpServerToolResponse200ResultStructuredContent | Unset = UNSET
    content: list[CallMcpServerToolResponse200ResultContentItem] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_error = self.is_error

        error_code = self.error_code

        error_message = self.error_message

        structured_content: dict[str, Any] | Unset = UNSET
        if not isinstance(self.structured_content, Unset):
            structured_content = self.structured_content.to_dict()

        content: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.content, Unset):
            content = []
            for content_item_data in self.content:
                content_item = content_item_data.to_dict()
                content.append(content_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_error is not UNSET:
            field_dict["isError"] = is_error
        if error_code is not UNSET:
            field_dict["errorCode"] = error_code
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if structured_content is not UNSET:
            field_dict["structuredContent"] = structured_content
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.call_mcp_server_tool_response_200_result_content_item import (
            CallMcpServerToolResponse200ResultContentItem,
        )
        from ..models.call_mcp_server_tool_response_200_result_structured_content import (
            CallMcpServerToolResponse200ResultStructuredContent,
        )

        d = dict(src_dict)
        is_error = d.pop("isError", UNSET)

        error_code = d.pop("errorCode", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        _structured_content = d.pop("structuredContent", UNSET)
        structured_content: CallMcpServerToolResponse200ResultStructuredContent | Unset
        if isinstance(_structured_content, Unset):
            structured_content = UNSET
        else:
            structured_content = CallMcpServerToolResponse200ResultStructuredContent.from_dict(_structured_content)

        _content = d.pop("content", UNSET)
        content: list[CallMcpServerToolResponse200ResultContentItem] | Unset = UNSET
        if _content is not UNSET:
            content = []
            for content_item_data in _content:
                content_item = CallMcpServerToolResponse200ResultContentItem.from_dict(content_item_data)

                content.append(content_item)

        call_mcp_server_tool_response_200_result = cls(
            is_error=is_error,
            error_code=error_code,
            error_message=error_message,
            structured_content=structured_content,
            content=content,
        )

        return call_mcp_server_tool_response_200_result
