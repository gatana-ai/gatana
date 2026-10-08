from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_923 import Schema923

T = TypeVar("T", bound="SecretStoreResponse")


@_attrs_define
class SecretStoreResponse:
    """
    Attributes:
        id (str):
        name (str):
        type_ (Schema923):
        is_enabled (bool):
        created_at (str):
        updated_at (str):
    """

    id: str
    name: str
    type_: Schema923
    is_enabled: bool
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        type_ = self.type_.value

        is_enabled = self.is_enabled

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "type": type_,
                "isEnabled": is_enabled,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        type_ = Schema923(d.pop("type"))

        is_enabled = d.pop("isEnabled")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        secret_store_response = cls(
            id=id,
            name=name,
            type_=type_,
            is_enabled=is_enabled,
            created_at=created_at,
            updated_at=updated_at,
        )

        return secret_store_response
