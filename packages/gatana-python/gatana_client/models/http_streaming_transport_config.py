from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HttpStreamingTransportConfig")


@_attrs_define
class HttpStreamingTransportConfig:
    """
    Attributes:
        type_ (Literal['httpstreaming']): Transport type discriminator, always "httpstreaming"
        url (str): URL of the MCP streamable HTTP endpoint
        headers (list[list[str]] | Unset):
    """

    type_: Literal["httpstreaming"]
    url: str
    headers: list[list[str]] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        url = self.url

        headers: list[list[str]] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = []
            for componentsschemas_schema65_item_data in self.headers:
                componentsschemas_schema65_item = []
                for componentsschemas_schema65_item_item_data in componentsschemas_schema65_item_data:
                    componentsschemas_schema65_item_item: str
                    componentsschemas_schema65_item_item = componentsschemas_schema65_item_item_data
                    componentsschemas_schema65_item.append(componentsschemas_schema65_item_item)

                headers.append(componentsschemas_schema65_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "url": url,
            }
        )
        if headers is not UNSET:
            field_dict["headers"] = headers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["httpstreaming"], d.pop("type"))
        if type_ != "httpstreaming":
            raise ValueError(f"type must match const 'httpstreaming', got '{type_}'")

        url = d.pop("url")

        _headers = d.pop("headers", UNSET)
        headers: list[list[str]] | Unset = UNSET
        if _headers is not UNSET:
            headers = []
            for componentsschemas_schema65_item_data in _headers:
                componentsschemas_schema65_item = []
                _componentsschemas_schema65_item = componentsschemas_schema65_item_data
                for componentsschemas_schema65_item_item_data in _componentsschemas_schema65_item:

                    def _parse_componentsschemas_schema65_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema65_item_item = _parse_componentsschemas_schema65_item_item(
                        componentsschemas_schema65_item_item_data
                    )

                    componentsschemas_schema65_item.append(componentsschemas_schema65_item_item)

                headers.append(componentsschemas_schema65_item)

        http_streaming_transport_config = cls(
            type_=type_,
            url=url,
            headers=headers,
        )

        http_streaming_transport_config.additional_properties = d
        return http_streaming_transport_config

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
