from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_605_endpoints_item import Schema605EndpointsItem


T = TypeVar("T", bound="Schema605")


@_attrs_define
class Schema605:
    """
    Attributes:
        success (bool):
        title (str): The title of the API as declared in the spec info object.
        version (str): The API version as declared in the spec info object.
        spec_version (str): The OpenAPI/Swagger specification version (e.g. "3.0.0", "2.0").
        base_url (str): The base URL of the API as declared in the spec servers object or basePath.
        operation_count (int): The number of operations (paths x methods) in the spec.
        endpoints (list[Schema605EndpointsItem]):
    """

    success: bool
    title: str
    version: str
    spec_version: str
    base_url: str
    operation_count: int
    endpoints: list[Schema605EndpointsItem]

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        title = self.title

        version = self.version

        spec_version = self.spec_version

        base_url = self.base_url

        operation_count = self.operation_count

        endpoints = []
        for endpoints_item_data in self.endpoints:
            endpoints_item = endpoints_item_data.to_dict()
            endpoints.append(endpoints_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "success": success,
                "title": title,
                "version": version,
                "specVersion": spec_version,
                "baseUrl": base_url,
                "operationCount": operation_count,
                "endpoints": endpoints,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_605_endpoints_item import Schema605EndpointsItem

        d = dict(src_dict)
        success = d.pop("success")

        title = d.pop("title")

        version = d.pop("version")

        spec_version = d.pop("specVersion")

        base_url = d.pop("baseUrl")

        operation_count = d.pop("operationCount")

        endpoints = []
        _endpoints = d.pop("endpoints")
        for endpoints_item_data in _endpoints:
            endpoints_item = Schema605EndpointsItem.from_dict(endpoints_item_data)

            endpoints.append(endpoints_item)

        schema_605 = cls(
            success=success,
            title=title,
            version=version,
            spec_version=spec_version,
            base_url=base_url,
            operation_count=operation_count,
            endpoints=endpoints,
        )

        return schema_605
