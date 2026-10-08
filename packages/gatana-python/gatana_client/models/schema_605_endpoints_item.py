from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema605EndpointsItem")


@_attrs_define
class Schema605EndpointsItem:
    """
    Attributes:
        method (str): The HTTP method of the endpoint (e.g. GET, POST).
        path (str): The path of the endpoint (e.g. /users/{id}).
    """

    method: str
    path: str

    def to_dict(self) -> dict[str, Any]:
        method = self.method

        path = self.path

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "method": method,
                "path": path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        method = d.pop("method")

        path = d.pop("path")

        schema_605_endpoints_item = cls(
            method=method,
            path=path,
        )

        return schema_605_endpoints_item
