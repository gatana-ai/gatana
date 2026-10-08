from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.audit_log_filter_option import AuditLogFilterOption


T = TypeVar("T", bound="AuditLogFilterOptions")


@_attrs_define
class AuditLogFilterOptions:
    """
    Attributes:
        event_name (list[AuditLogFilterOption]):
        entity_type (list[AuditLogFilterOption]):
        client_id (list[AuditLogFilterOption]):
        pat_id (list[AuditLogFilterOption]):
        tool_name (list[AuditLogFilterOption]):
    """

    event_name: list[AuditLogFilterOption]
    entity_type: list[AuditLogFilterOption]
    client_id: list[AuditLogFilterOption]
    pat_id: list[AuditLogFilterOption]
    tool_name: list[AuditLogFilterOption]

    def to_dict(self) -> dict[str, Any]:
        event_name = []
        for componentsschemas_schema373_item_data in self.event_name:
            componentsschemas_schema373_item = componentsschemas_schema373_item_data.to_dict()
            event_name.append(componentsschemas_schema373_item)

        entity_type = []
        for componentsschemas_schema378_item_data in self.entity_type:
            componentsschemas_schema378_item = componentsschemas_schema378_item_data.to_dict()
            entity_type.append(componentsschemas_schema378_item)

        client_id = []
        for componentsschemas_schema379_item_data in self.client_id:
            componentsschemas_schema379_item = componentsschemas_schema379_item_data.to_dict()
            client_id.append(componentsschemas_schema379_item)

        pat_id = []
        for componentsschemas_schema380_item_data in self.pat_id:
            componentsschemas_schema380_item = componentsschemas_schema380_item_data.to_dict()
            pat_id.append(componentsschemas_schema380_item)

        tool_name = []
        for componentsschemas_schema381_item_data in self.tool_name:
            componentsschemas_schema381_item = componentsschemas_schema381_item_data.to_dict()
            tool_name.append(componentsschemas_schema381_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "eventName": event_name,
                "entityType": entity_type,
                "clientId": client_id,
                "patId": pat_id,
                "toolName": tool_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audit_log_filter_option import AuditLogFilterOption

        d = dict(src_dict)
        event_name = []
        _event_name = d.pop("eventName")
        for componentsschemas_schema373_item_data in _event_name:
            componentsschemas_schema373_item = AuditLogFilterOption.from_dict(componentsschemas_schema373_item_data)

            event_name.append(componentsschemas_schema373_item)

        entity_type = []
        _entity_type = d.pop("entityType")
        for componentsschemas_schema378_item_data in _entity_type:
            componentsschemas_schema378_item = AuditLogFilterOption.from_dict(componentsschemas_schema378_item_data)

            entity_type.append(componentsschemas_schema378_item)

        client_id = []
        _client_id = d.pop("clientId")
        for componentsschemas_schema379_item_data in _client_id:
            componentsschemas_schema379_item = AuditLogFilterOption.from_dict(componentsschemas_schema379_item_data)

            client_id.append(componentsschemas_schema379_item)

        pat_id = []
        _pat_id = d.pop("patId")
        for componentsschemas_schema380_item_data in _pat_id:
            componentsschemas_schema380_item = AuditLogFilterOption.from_dict(componentsschemas_schema380_item_data)

            pat_id.append(componentsschemas_schema380_item)

        tool_name = []
        _tool_name = d.pop("toolName")
        for componentsschemas_schema381_item_data in _tool_name:
            componentsschemas_schema381_item = AuditLogFilterOption.from_dict(componentsschemas_schema381_item_data)

            tool_name.append(componentsschemas_schema381_item)

        audit_log_filter_options = cls(
            event_name=event_name,
            entity_type=entity_type,
            client_id=client_id,
            pat_id=pat_id,
            tool_name=tool_name,
        )

        return audit_log_filter_options
