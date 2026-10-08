from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_967 import Schema967

T = TypeVar("T", bound="Schema983")


@_attrs_define
class Schema983:
    """
    Attributes:
        id (str): Unique ID of the destination
        name (str): Display name of the destination
        url (str): HTTPS endpoint that receives the NDJSON batches
        auth_header_name (None | str): Name of the custom auth header, or null when none is configured
        has_auth_header_value (bool): Whether a custom auth header value is stored. The value itself is never returned
        is_enabled (bool): The tenant admin's on/off switch
        status (Schema967): Delivery status, maintained by the export job
        export_audit_logs (bool): Whether audit log events are streamed
        export_credential_audit_logs (bool): Whether credential audit log events are streamed
        consecutive_failures (float): Number of delivery attempts that failed in a row
        failing_since (None | str): Time when the current failure streak started, or null
        next_attempt_at (None | str): Time of the next delivery attempt, or null
        last_attempt_at (None | str): Time of the last delivery attempt, or null
        last_success_at (None | str): Time of the last successful delivery, or null
        last_error (None | str): Message of the last delivery error, or null
        created_at (str): Time when the destination was created
        updated_at (str): Time when the destination was last updated
    """

    id: str
    name: str
    url: str
    auth_header_name: None | str
    has_auth_header_value: bool
    is_enabled: bool
    status: Schema967
    export_audit_logs: bool
    export_credential_audit_logs: bool
    consecutive_failures: float
    failing_since: None | str
    next_attempt_at: None | str
    last_attempt_at: None | str
    last_success_at: None | str
    last_error: None | str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        url = self.url

        auth_header_name: None | str
        auth_header_name = self.auth_header_name

        has_auth_header_value = self.has_auth_header_value

        is_enabled = self.is_enabled

        status = self.status.value

        export_audit_logs = self.export_audit_logs

        export_credential_audit_logs = self.export_credential_audit_logs

        consecutive_failures = self.consecutive_failures

        failing_since: None | str
        failing_since = self.failing_since

        next_attempt_at: None | str
        next_attempt_at = self.next_attempt_at

        last_attempt_at: None | str
        last_attempt_at = self.last_attempt_at

        last_success_at: None | str
        last_success_at = self.last_success_at

        last_error: None | str
        last_error = self.last_error

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "url": url,
                "authHeaderName": auth_header_name,
                "hasAuthHeaderValue": has_auth_header_value,
                "isEnabled": is_enabled,
                "status": status,
                "exportAuditLogs": export_audit_logs,
                "exportCredentialAuditLogs": export_credential_audit_logs,
                "consecutiveFailures": consecutive_failures,
                "failingSince": failing_since,
                "nextAttemptAt": next_attempt_at,
                "lastAttemptAt": last_attempt_at,
                "lastSuccessAt": last_success_at,
                "lastError": last_error,
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

        url = d.pop("url")

        def _parse_auth_header_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        auth_header_name = _parse_auth_header_name(d.pop("authHeaderName"))

        has_auth_header_value = d.pop("hasAuthHeaderValue")

        is_enabled = d.pop("isEnabled")

        status = Schema967(d.pop("status"))

        export_audit_logs = d.pop("exportAuditLogs")

        export_credential_audit_logs = d.pop("exportCredentialAuditLogs")

        consecutive_failures = d.pop("consecutiveFailures")

        def _parse_failing_since(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        failing_since = _parse_failing_since(d.pop("failingSince"))

        def _parse_next_attempt_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_attempt_at = _parse_next_attempt_at(d.pop("nextAttemptAt"))

        def _parse_last_attempt_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_attempt_at = _parse_last_attempt_at(d.pop("lastAttemptAt"))

        def _parse_last_success_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_success_at = _parse_last_success_at(d.pop("lastSuccessAt"))

        def _parse_last_error(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_error = _parse_last_error(d.pop("lastError"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        schema_983 = cls(
            id=id,
            name=name,
            url=url,
            auth_header_name=auth_header_name,
            has_auth_header_value=has_auth_header_value,
            is_enabled=is_enabled,
            status=status,
            export_audit_logs=export_audit_logs,
            export_credential_audit_logs=export_credential_audit_logs,
            consecutive_failures=consecutive_failures,
            failing_since=failing_since,
            next_attempt_at=next_attempt_at,
            last_attempt_at=last_attempt_at,
            last_success_at=last_success_at,
            last_error=last_error,
            created_at=created_at,
            updated_at=updated_at,
        )

        return schema_983
