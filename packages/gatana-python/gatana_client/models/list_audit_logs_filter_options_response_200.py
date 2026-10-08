from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.audit_log_filter_options import AuditLogFilterOptions


T = TypeVar("T", bound="ListAuditLogsFilterOptionsResponse200")


@_attrs_define
class ListAuditLogsFilterOptionsResponse200:
    """
    Attributes:
        options (AuditLogFilterOptions):
    """

    options: AuditLogFilterOptions

    def to_dict(self) -> dict[str, Any]:
        options = self.options.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "options": options,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audit_log_filter_options import AuditLogFilterOptions

        d = dict(src_dict)
        options = AuditLogFilterOptions.from_dict(d.pop("options"))

        list_audit_logs_filter_options_response_200 = cls(
            options=options,
        )

        return list_audit_logs_filter_options_response_200
