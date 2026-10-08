from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.secret_mapping_response import SecretMappingResponse


T = TypeVar("T", bound="SecretMappingListResponse")


@_attrs_define
class SecretMappingListResponse:
    """
    Attributes:
        mappings (list[SecretMappingResponse]):
    """

    mappings: list[SecretMappingResponse]

    def to_dict(self) -> dict[str, Any]:
        mappings = []
        for componentsschemas_schema951_item_data in self.mappings:
            componentsschemas_schema951_item = componentsschemas_schema951_item_data.to_dict()
            mappings.append(componentsschemas_schema951_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mappings": mappings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.secret_mapping_response import SecretMappingResponse

        d = dict(src_dict)
        mappings = []
        _mappings = d.pop("mappings")
        for componentsschemas_schema951_item_data in _mappings:
            componentsschemas_schema951_item = SecretMappingResponse.from_dict(componentsschemas_schema951_item_data)

            mappings.append(componentsschemas_schema951_item)

        secret_mapping_list_response = cls(
            mappings=mappings,
        )

        return secret_mapping_list_response
