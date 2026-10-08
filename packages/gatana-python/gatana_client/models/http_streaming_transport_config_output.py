from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="HttpStreamingTransportConfigOutput")


@_attrs_define
class HttpStreamingTransportConfigOutput:
    """
    Attributes:
        type_ (Literal['httpstreaming']): Transport type discriminator, always "httpstreaming"
        url (str): URL of the MCP streamable HTTP endpoint
        headers (list[list[str]] | Unset):
    """

    type_: Literal["httpstreaming"]
    url: str
    headers: list[list[str]] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        url = self.url

        headers: list[list[str]] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = []
            for componentsschemas_schema473_item_data in self.headers:
                componentsschemas_schema473_item = []
                for componentsschemas_schema473_item_item_data in componentsschemas_schema473_item_data:
                    componentsschemas_schema473_item_item: str
                    componentsschemas_schema473_item_item = componentsschemas_schema473_item_item_data
                    componentsschemas_schema473_item.append(componentsschemas_schema473_item_item)

                headers.append(componentsschemas_schema473_item)

        field_dict: dict[str, Any] = {}

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
            for componentsschemas_schema473_item_data in _headers:
                componentsschemas_schema473_item = []
                _componentsschemas_schema473_item = componentsschemas_schema473_item_data
                for componentsschemas_schema473_item_item_data in _componentsschemas_schema473_item:

                    def _parse_componentsschemas_schema473_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema473_item_item = _parse_componentsschemas_schema473_item_item(
                        componentsschemas_schema473_item_item_data
                    )

                    componentsschemas_schema473_item.append(componentsschemas_schema473_item_item)

                headers.append(componentsschemas_schema473_item)

        http_streaming_transport_config_output = cls(
            type_=type_,
            url=url,
            headers=headers,
        )

        return http_streaming_transport_config_output
