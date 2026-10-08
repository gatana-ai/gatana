from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CreateMcpServerFileResponse200")


@_attrs_define
class CreateMcpServerFileResponse200:
    """
    Attributes:
        id (str):
    """

    id: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        create_mcp_server_file_response_200 = cls(
            id=id,
        )

        return create_mcp_server_file_response_200
