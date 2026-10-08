from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ServerCredentialsApiKeys")


@_attrs_define
class ServerCredentialsApiKeys:
    """
    Attributes:
        type_ (Literal['apikey']): Credential type discriminator, always "apikey"
        apikeys (list[list[str]]): API keys as [name, value] pairs
    """

    type_: Literal["apikey"]
    apikeys: list[list[str]]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        apikeys = []
        for componentsschemas_schema178_item_data in self.apikeys:
            componentsschemas_schema178_item = []
            for componentsschemas_schema179_item_data in componentsschemas_schema178_item_data:
                componentsschemas_schema179_item: str
                componentsschemas_schema179_item = componentsschemas_schema179_item_data
                componentsschemas_schema178_item.append(componentsschemas_schema179_item)

            apikeys.append(componentsschemas_schema178_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "apikeys": apikeys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["apikey"], d.pop("type"))
        if type_ != "apikey":
            raise ValueError(f"type must match const 'apikey', got '{type_}'")

        apikeys = []
        _apikeys = d.pop("apikeys")
        for componentsschemas_schema178_item_data in _apikeys:
            componentsschemas_schema178_item = []
            _componentsschemas_schema178_item = componentsschemas_schema178_item_data
            for componentsschemas_schema179_item_data in _componentsschemas_schema178_item:

                def _parse_componentsschemas_schema179_item(data: object) -> str:
                    return cast(str, data)

                componentsschemas_schema179_item = _parse_componentsschemas_schema179_item(
                    componentsschemas_schema179_item_data
                )

                componentsschemas_schema178_item.append(componentsschemas_schema179_item)

            apikeys.append(componentsschemas_schema178_item)

        server_credentials_api_keys = cls(
            type_=type_,
            apikeys=apikeys,
        )

        server_credentials_api_keys.additional_properties = d
        return server_credentials_api_keys

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
