from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetMcpServersAccessPreviewResponse200")


@_attrs_define
class GetMcpServersAccessPreviewResponse200:
    """
    Attributes:
        accessible_server_ids (list[str]):
    """

    accessible_server_ids: list[str]

    def to_dict(self) -> dict[str, Any]:
        accessible_server_ids = self.accessible_server_ids

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "accessibleServerIds": accessible_server_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        accessible_server_ids = cast(list[str], d.pop("accessibleServerIds"))

        get_mcp_servers_access_preview_response_200 = cls(
            accessible_server_ids=accessible_server_ids,
        )

        return get_mcp_servers_access_preview_response_200
