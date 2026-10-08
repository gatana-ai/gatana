from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_442 import Schema442

T = TypeVar("T", bound="UserIdentity")


@_attrs_define
class UserIdentity:
    """
    Attributes:
        tenant_id (float): ID of the tenant that owns the identity
        external_id (str): Identifier of the user at the identity provider
        user_id (str): ID of the user the identity belongs to
        type_ (Schema442): Type of the identity: external-oidc, external-saml, or native
        created_at (str): Time when the identity was created
        updated_at (str): Time when the identity was last updated
    """

    tenant_id: float
    external_id: str
    user_id: str
    type_: Schema442
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        external_id = self.external_id

        user_id = self.user_id

        type_ = self.type_.value

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tenantId": tenant_id,
                "externalId": external_id,
                "userId": user_id,
                "type": type_,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = d.pop("tenantId")

        external_id = d.pop("externalId")

        user_id = d.pop("userId")

        type_ = Schema442(d.pop("type"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        user_identity = cls(
            tenant_id=tenant_id,
            external_id=external_id,
            user_id=user_id,
            type_=type_,
            created_at=created_at,
            updated_at=updated_at,
        )

        return user_identity
