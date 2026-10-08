from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema122ResourceType0")


@_attrs_define
class Schema122ResourceType0:
    """
    Attributes:
        id (str | Unset):
        available_scopes (list[str] | Unset):
        metadata_url (str | Unset):
    """

    id: str | Unset = UNSET
    available_scopes: list[str] | Unset = UNSET
    metadata_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        available_scopes: list[str] | Unset = UNSET
        if not isinstance(self.available_scopes, Unset):
            available_scopes = self.available_scopes

        metadata_url = self.metadata_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if available_scopes is not UNSET:
            field_dict["availableScopes"] = available_scopes
        if metadata_url is not UNSET:
            field_dict["metadataUrl"] = metadata_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        available_scopes = cast(list[str], d.pop("availableScopes", UNSET))

        metadata_url = d.pop("metadataUrl", UNSET)

        schema_122_resource_type_0 = cls(
            id=id,
            available_scopes=available_scopes,
            metadata_url=metadata_url,
        )

        schema_122_resource_type_0.additional_properties = d
        return schema_122_resource_type_0

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
