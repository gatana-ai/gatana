from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema1065")


@_attrs_define
class Schema1065:
    """
    Attributes:
        id (str): Unique ID of the token
        tenant_id (str): ID of the tenant that owns the token
        name (str): Display name of the token
        last_used_at (None | str): Time when the token was last used, or null if never used
        token_hash (str): Hash of the token secret
        created_at (str): Time when the token was created
        updated_at (str): Time when the token was last updated
        token (str | Unset):
    """

    id: str
    tenant_id: str
    name: str
    last_used_at: None | str
    token_hash: str
    created_at: str
    updated_at: str
    token: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        name = self.name

        last_used_at: None | str
        last_used_at = self.last_used_at

        token_hash = self.token_hash

        created_at = self.created_at

        updated_at = self.updated_at

        token = self.token

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "name": name,
                "lastUsedAt": last_used_at,
                "tokenHash": token_hash,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        name = d.pop("name")

        def _parse_last_used_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_used_at = _parse_last_used_at(d.pop("lastUsedAt"))

        token_hash = d.pop("tokenHash")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        token = d.pop("token", UNSET)

        schema_1065 = cls(
            id=id,
            tenant_id=tenant_id,
            name=name,
            last_used_at=last_used_at,
            token_hash=token_hash,
            created_at=created_at,
            updated_at=updated_at,
            token=token,
        )

        return schema_1065
