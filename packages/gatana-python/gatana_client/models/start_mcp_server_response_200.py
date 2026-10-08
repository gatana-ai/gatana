from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="StartMcpServerResponse200")


@_attrs_define
class StartMcpServerResponse200:
    """
    Attributes:
        success (bool):
        detail (str | Unset):
    """

    success: bool
    detail: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        detail = self.detail

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "success": success,
            }
        )
        if detail is not UNSET:
            field_dict["detail"] = detail

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        detail = d.pop("detail", UNSET)

        start_mcp_server_response_200 = cls(
            success=success,
            detail=detail,
        )

        return start_mcp_server_response_200
