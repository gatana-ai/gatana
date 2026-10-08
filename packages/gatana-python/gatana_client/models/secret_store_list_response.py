from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.secret_store_response import SecretStoreResponse


T = TypeVar("T", bound="SecretStoreListResponse")


@_attrs_define
class SecretStoreListResponse:
    """
    Attributes:
        stores (list[SecretStoreResponse]):
    """

    stores: list[SecretStoreResponse]

    def to_dict(self) -> dict[str, Any]:
        stores = []
        for componentsschemas_schema920_item_data in self.stores:
            componentsschemas_schema920_item = componentsschemas_schema920_item_data.to_dict()
            stores.append(componentsschemas_schema920_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "stores": stores,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.secret_store_response import SecretStoreResponse

        d = dict(src_dict)
        stores = []
        _stores = d.pop("stores")
        for componentsschemas_schema920_item_data in _stores:
            componentsschemas_schema920_item = SecretStoreResponse.from_dict(componentsschemas_schema920_item_data)

            stores.append(componentsschemas_schema920_item)

        secret_store_list_response = cls(
            stores=stores,
        )

        return secret_store_list_response
