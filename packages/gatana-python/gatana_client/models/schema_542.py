from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema542")


@_attrs_define
class Schema542:
    """
    Attributes:
        id (str):
        available_scopes (list[str]):
        metadata_url (str):
    """

    id: str
    available_scopes: list[str]
    metadata_url: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        available_scopes = self.available_scopes

        metadata_url = self.metadata_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "availableScopes": available_scopes,
                "metadataUrl": metadata_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        available_scopes = cast(list[str], d.pop("availableScopes"))

        metadata_url = d.pop("metadataUrl")

        schema_542 = cls(
            id=id,
            available_scopes=available_scopes,
            metadata_url=metadata_url,
        )

        return schema_542
