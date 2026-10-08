from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="ListMcpServerCredentialsProfileApikeysResponse200")


@_attrs_define
class ListMcpServerCredentialsProfileApikeysResponse200:
    """
    Attributes:
        apikeys (list[list[str]]):
    """

    apikeys: list[list[str]]

    def to_dict(self) -> dict[str, Any]:
        apikeys = []
        for apikeys_item_data in self.apikeys:
            apikeys_item = []
            for apikeys_item_item_data in apikeys_item_data:
                apikeys_item_item: str
                apikeys_item_item = apikeys_item_item_data
                apikeys_item.append(apikeys_item_item)

            apikeys.append(apikeys_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "apikeys": apikeys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        apikeys = []
        _apikeys = d.pop("apikeys")
        for apikeys_item_data in _apikeys:
            apikeys_item = []
            _apikeys_item = apikeys_item_data
            for apikeys_item_item_data in _apikeys_item:

                def _parse_apikeys_item_item(data: object) -> str:
                    return cast(str, data)

                apikeys_item_item = _parse_apikeys_item_item(apikeys_item_item_data)

                apikeys_item.append(apikeys_item_item)

            apikeys.append(apikeys_item)

        list_mcp_server_credentials_profile_apikeys_response_200 = cls(
            apikeys=apikeys,
        )

        return list_mcp_server_credentials_profile_apikeys_response_200
