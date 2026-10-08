from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="SecretMappingResponse")



@_attrs_define
class SecretMappingResponse:
    """ 
        Attributes:
            name (str):
            secret_identifier (str):
            created_at (str):
            updated_at (str):
     """

    name: str
    secret_identifier: str
    created_at: str
    updated_at: str





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        secret_identifier = self.secret_identifier

        created_at = self.created_at

        updated_at = self.updated_at


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "name": name,
            "secretIdentifier": secret_identifier,
            "createdAt": created_at,
            "updatedAt": updated_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        secret_identifier = d.pop("secretIdentifier")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        secret_mapping_response = cls(
            name=name,
            secret_identifier=secret_identifier,
            created_at=created_at,
            updated_at=updated_at,
        )

        return secret_mapping_response

