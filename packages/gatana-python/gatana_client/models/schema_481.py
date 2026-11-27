from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_482 import Schema482
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema481")


@_attrs_define
class Schema481:
    """
    Attributes:
        id (str):
        tenant_id (str):
        name (str):
        api_key (str):
        email (str):
        role (Schema482):
        is_service_account (bool):
        created_at (str):
        updated_at (str):
        is_super_administrator (bool | Unset):
    """

    id: str
    tenant_id: str
    name: str
    api_key: str
    email: str
    role: Schema482
    is_service_account: bool
    created_at: str
    updated_at: str
    is_super_administrator: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        name = self.name

        api_key = self.api_key

        email = self.email

        role = self.role.value

        is_service_account = self.is_service_account

        created_at = self.created_at

        updated_at = self.updated_at

        is_super_administrator = self.is_super_administrator

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "name": name,
                "apiKey": api_key,
                "email": email,
                "role": role,
                "isServiceAccount": is_service_account,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if is_super_administrator is not UNSET:
            field_dict["isSuperAdministrator"] = is_super_administrator

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        name = d.pop("name")

        api_key = d.pop("apiKey")

        email = d.pop("email")

        role = Schema482(d.pop("role"))

        is_service_account = d.pop("isServiceAccount")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        is_super_administrator = d.pop("isSuperAdministrator", UNSET)

        schema_481 = cls(
            id=id,
            tenant_id=tenant_id,
            name=name,
            api_key=api_key,
            email=email,
            role=role,
            is_service_account=is_service_account,
            created_at=created_at,
            updated_at=updated_at,
            is_super_administrator=is_super_administrator,
        )

        return schema_481
