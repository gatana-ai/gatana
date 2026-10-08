from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="UpdateMcpServerFileNameResponse200")


@_attrs_define
class UpdateMcpServerFileNameResponse200:
    """
    Attributes:
        success (bool):
    """

    success: bool

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "success": success,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        update_mcp_server_file_name_response_200 = cls(
            success=success,
        )

        return update_mcp_server_file_name_response_200
