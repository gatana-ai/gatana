from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_43 import Schema43
from ..models.schema_47 import Schema47
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateServerRequest")


@_attrs_define
class CreateServerRequest:
    """
    Attributes:
        transport_type (Schema43): Transport type: httpstreaming, sse, stdio, hosted, or openapi
        slug (str): Technical identifier.
        is_output_compression_enabled (bool | Unset):
        visibility (Schema47 | Unset):
    """

    transport_type: Schema43
    slug: str
    is_output_compression_enabled: bool | Unset = UNSET
    visibility: Schema47 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        transport_type = self.transport_type.value

        slug = self.slug

        is_output_compression_enabled = self.is_output_compression_enabled

        visibility: str | Unset = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "transportType": transport_type,
                "slug": slug,
            }
        )
        if is_output_compression_enabled is not UNSET:
            field_dict["isOutputCompressionEnabled"] = is_output_compression_enabled
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        transport_type = Schema43(d.pop("transportType"))

        slug = d.pop("slug")

        is_output_compression_enabled = d.pop("isOutputCompressionEnabled", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: Schema47 | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = Schema47(_visibility)

        create_server_request = cls(
            transport_type=transport_type,
            slug=slug,
            is_output_compression_enabled=is_output_compression_enabled,
            visibility=visibility,
        )

        create_server_request.additional_properties = d
        return create_server_request

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
