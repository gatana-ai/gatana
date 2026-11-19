from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.audit_log_response import AuditLogResponse
    from ..models.schema_536 import Schema536


T = TypeVar("T", bound="PaginatedAuditLogResponse")


@_attrs_define
class PaginatedAuditLogResponse:
    """
    Attributes:
        pagination (Schema536): Pagination metadata
        data (list[AuditLogResponse]): Items on the current page
    """

    pagination: Schema536
    data: list[AuditLogResponse]

    def to_dict(self) -> dict[str, Any]:
        pagination = self.pagination.to_dict()

        data = []
        for componentsschemas_schema543_item_data in self.data:
            componentsschemas_schema543_item = componentsschemas_schema543_item_data.to_dict()
            data.append(componentsschemas_schema543_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "pagination": pagination,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audit_log_response import AuditLogResponse
        from ..models.schema_536 import Schema536

        d = dict(src_dict)
        pagination = Schema536.from_dict(d.pop("pagination"))

        data = []
        _data = d.pop("data")
        for componentsschemas_schema543_item_data in _data:
            componentsschemas_schema543_item = AuditLogResponse.from_dict(componentsschemas_schema543_item_data)

            data.append(componentsschemas_schema543_item)

        paginated_audit_log_response = cls(
            pagination=pagination,
            data=data,
        )

        return paginated_audit_log_response
