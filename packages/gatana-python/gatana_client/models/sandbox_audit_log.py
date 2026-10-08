from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1051 import Schema1051


T = TypeVar("T", bound="SandboxAuditLog")


@_attrs_define
class SandboxAuditLog:
    """
    Attributes:
        id (float):
        tenant_id (str):
        sandbox_id (str):
        event_name (str):
        details (Schema1051):
        created_at (str):
    """

    id: float
    tenant_id: str
    sandbox_id: str
    event_name: str
    details: Schema1051
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        sandbox_id = self.sandbox_id

        event_name = self.event_name

        details = self.details.to_dict()

        created_at = self.created_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "sandboxId": sandbox_id,
                "eventName": event_name,
                "details": details,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1051 import Schema1051

        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        sandbox_id = d.pop("sandboxId")

        event_name = d.pop("eventName")

        details = Schema1051.from_dict(d.pop("details"))

        created_at = d.pop("createdAt")

        sandbox_audit_log = cls(
            id=id,
            tenant_id=tenant_id,
            sandbox_id=sandbox_id,
            event_name=event_name,
            details=details,
            created_at=created_at,
        )

        return sandbox_audit_log
