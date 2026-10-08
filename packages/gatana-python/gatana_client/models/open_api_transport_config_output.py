from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_516 import Schema516
from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenApiTransportConfigOutput")


@_attrs_define
class OpenApiTransportConfigOutput:
    """
    Attributes:
        type_ (Literal['openapi']): Transport type discriminator, always "openapi"
        method (Schema516): How the OpenAPI spec is supplied: from a URL or as inline content
        spec_url (Literal[''] | str):
        spec (str):
        base_url (Literal[''] | str):
        headers (list[list[str]] | Unset):
    """

    type_: Literal["openapi"]
    method: Schema516
    spec_url: Literal[""] | str
    spec: str
    base_url: Literal[""] | str
    headers: list[list[str]] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        method = self.method.value

        spec_url: Literal[""] | str
        spec_url = self.spec_url

        spec = self.spec

        base_url: Literal[""] | str
        base_url = self.base_url

        headers: list[list[str]] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = []
            for componentsschemas_schema523_item_data in self.headers:
                componentsschemas_schema523_item = []
                for componentsschemas_schema523_item_item_data in componentsschemas_schema523_item_data:
                    componentsschemas_schema523_item_item: str
                    componentsschemas_schema523_item_item = componentsschemas_schema523_item_item_data
                    componentsschemas_schema523_item.append(componentsschemas_schema523_item_item)

                headers.append(componentsschemas_schema523_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "method": method,
                "specUrl": spec_url,
                "spec": spec,
                "baseUrl": base_url,
            }
        )
        if headers is not UNSET:
            field_dict["headers"] = headers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["openapi"], d.pop("type"))
        if type_ != "openapi":
            raise ValueError(f"type must match const 'openapi', got '{type_}'")

        method = Schema516(d.pop("method"))

        def _parse_spec_url(data: object) -> Literal[""] | str:
            componentsschemas_schema517_type_1 = cast(Literal[""], data)
            if componentsschemas_schema517_type_1 != "":
                raise ValueError(
                    f"/components/schemas/__schema517_type_1 must match const '', got '{componentsschemas_schema517_type_1}'"
                )
            return componentsschemas_schema517_type_1
            return cast(Literal[""] | str, data)

        spec_url = _parse_spec_url(d.pop("specUrl"))

        spec = d.pop("spec")

        def _parse_base_url(data: object) -> Literal[""] | str:
            componentsschemas_schema521_type_1 = cast(Literal[""], data)
            if componentsschemas_schema521_type_1 != "":
                raise ValueError(
                    f"/components/schemas/__schema521_type_1 must match const '', got '{componentsschemas_schema521_type_1}'"
                )
            return componentsschemas_schema521_type_1
            return cast(Literal[""] | str, data)

        base_url = _parse_base_url(d.pop("baseUrl"))

        _headers = d.pop("headers", UNSET)
        headers: list[list[str]] | Unset = UNSET
        if _headers is not UNSET:
            headers = []
            for componentsschemas_schema523_item_data in _headers:
                componentsschemas_schema523_item = []
                _componentsschemas_schema523_item = componentsschemas_schema523_item_data
                for componentsschemas_schema523_item_item_data in _componentsschemas_schema523_item:

                    def _parse_componentsschemas_schema523_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema523_item_item = _parse_componentsschemas_schema523_item_item(
                        componentsschemas_schema523_item_item_data
                    )

                    componentsschemas_schema523_item.append(componentsschemas_schema523_item_item)

                headers.append(componentsschemas_schema523_item)

        open_api_transport_config_output = cls(
            type_=type_,
            method=method,
            spec_url=spec_url,
            spec=spec,
            base_url=base_url,
            headers=headers,
        )

        return open_api_transport_config_output
