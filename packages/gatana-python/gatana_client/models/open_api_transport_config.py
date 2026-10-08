from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_112 import Schema112
from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenApiTransportConfig")


@_attrs_define
class OpenApiTransportConfig:
    """
    Attributes:
        type_ (Literal['openapi']): Transport type discriminator, always "openapi"
        method (Schema112): How the OpenAPI spec is supplied: from a URL or as inline content
        spec_url (Literal[''] | str | Unset):
        spec (str | Unset):
        base_url (Literal[''] | str | Unset):
        headers (list[list[str]] | Unset):
    """

    type_: Literal["openapi"]
    method: Schema112
    spec_url: Literal[""] | str | Unset = UNSET
    spec: str | Unset = UNSET
    base_url: Literal[""] | str | Unset = UNSET
    headers: list[list[str]] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        method = self.method.value

        spec_url: Literal[""] | str | Unset
        if isinstance(self.spec_url, Unset):
            spec_url = UNSET
        else:
            spec_url = self.spec_url

        spec = self.spec

        base_url: Literal[""] | str | Unset
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        headers: list[list[str]] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = []
            for componentsschemas_schema119_item_data in self.headers:
                componentsschemas_schema119_item = []
                for componentsschemas_schema119_item_item_data in componentsschemas_schema119_item_data:
                    componentsschemas_schema119_item_item: str
                    componentsschemas_schema119_item_item = componentsschemas_schema119_item_item_data
                    componentsschemas_schema119_item.append(componentsschemas_schema119_item_item)

                headers.append(componentsschemas_schema119_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "method": method,
            }
        )
        if spec_url is not UNSET:
            field_dict["specUrl"] = spec_url
        if spec is not UNSET:
            field_dict["spec"] = spec
        if base_url is not UNSET:
            field_dict["baseUrl"] = base_url
        if headers is not UNSET:
            field_dict["headers"] = headers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["openapi"], d.pop("type"))
        if type_ != "openapi":
            raise ValueError(f"type must match const 'openapi', got '{type_}'")

        method = Schema112(d.pop("method"))

        def _parse_spec_url(data: object) -> Literal[""] | str | Unset:
            if isinstance(data, Unset):
                return data
            componentsschemas_schema113_type_1 = cast(Literal[""], data)
            if componentsschemas_schema113_type_1 != "":
                raise ValueError(
                    f"/components/schemas/__schema113_type_1 must match const '', got '{componentsschemas_schema113_type_1}'"
                )
            return componentsschemas_schema113_type_1
            return cast(Literal[""] | str | Unset, data)

        spec_url = _parse_spec_url(d.pop("specUrl", UNSET))

        spec = d.pop("spec", UNSET)

        def _parse_base_url(data: object) -> Literal[""] | str | Unset:
            if isinstance(data, Unset):
                return data
            componentsschemas_schema117_type_1 = cast(Literal[""], data)
            if componentsschemas_schema117_type_1 != "":
                raise ValueError(
                    f"/components/schemas/__schema117_type_1 must match const '', got '{componentsschemas_schema117_type_1}'"
                )
            return componentsschemas_schema117_type_1
            return cast(Literal[""] | str | Unset, data)

        base_url = _parse_base_url(d.pop("baseUrl", UNSET))

        _headers = d.pop("headers", UNSET)
        headers: list[list[str]] | Unset = UNSET
        if _headers is not UNSET:
            headers = []
            for componentsschemas_schema119_item_data in _headers:
                componentsschemas_schema119_item = []
                _componentsschemas_schema119_item = componentsschemas_schema119_item_data
                for componentsschemas_schema119_item_item_data in _componentsschemas_schema119_item:

                    def _parse_componentsschemas_schema119_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema119_item_item = _parse_componentsschemas_schema119_item_item(
                        componentsschemas_schema119_item_item_data
                    )

                    componentsschemas_schema119_item.append(componentsschemas_schema119_item_item)

                headers.append(componentsschemas_schema119_item)

        open_api_transport_config = cls(
            type_=type_,
            method=method,
            spec_url=spec_url,
            spec=spec,
            base_url=base_url,
            headers=headers,
        )

        open_api_transport_config.additional_properties = d
        return open_api_transport_config

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
