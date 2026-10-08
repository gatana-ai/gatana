from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="AuditLogResponse")


@_attrs_define
class AuditLogResponse:
    """
    Attributes:
        id (float):
        tenant_id (str):
        event_time (str):
        entity_type (None | str):
        entity_id (None | str):
        event_name (str):
        user_id (None | str):
        details (Any):
        only_superadmin_visibility (bool):
        created_at (str):
        user_full_name (str):
        user_email (None | str):
        team_name (None | str):
        server_slug (None | str):
        profile_name (None | str):
    """

    id: float
    tenant_id: str
    event_time: str
    entity_type: None | str
    entity_id: None | str
    event_name: str
    user_id: None | str
    details: Any
    only_superadmin_visibility: bool
    created_at: str
    user_full_name: str
    user_email: None | str
    team_name: None | str
    server_slug: None | str
    profile_name: None | str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        event_time = self.event_time

        entity_type: None | str
        entity_type = self.entity_type

        entity_id: None | str
        entity_id = self.entity_id

        event_name = self.event_name

        user_id: None | str
        user_id = self.user_id

        details = self.details

        only_superadmin_visibility = self.only_superadmin_visibility

        created_at = self.created_at

        user_full_name = self.user_full_name

        user_email: None | str
        user_email = self.user_email

        team_name: None | str
        team_name = self.team_name

        server_slug: None | str
        server_slug = self.server_slug

        profile_name: None | str
        profile_name = self.profile_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "eventTime": event_time,
                "entityType": entity_type,
                "entityId": entity_id,
                "eventName": event_name,
                "userId": user_id,
                "details": details,
                "onlySuperadminVisibility": only_superadmin_visibility,
                "createdAt": created_at,
                "userFullName": user_full_name,
                "userEmail": user_email,
                "teamName": team_name,
                "serverSlug": server_slug,
                "profileName": profile_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        event_time = d.pop("eventTime")

        def _parse_entity_type(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        entity_type = _parse_entity_type(d.pop("entityType"))

        def _parse_entity_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        entity_id = _parse_entity_id(d.pop("entityId"))

        event_name = d.pop("eventName")

        def _parse_user_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        user_id = _parse_user_id(d.pop("userId"))

        details = d.pop("details")

        only_superadmin_visibility = d.pop("onlySuperadminVisibility")

        created_at = d.pop("createdAt")

        user_full_name = d.pop("userFullName")

        def _parse_user_email(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        user_email = _parse_user_email(d.pop("userEmail"))

        def _parse_team_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        team_name = _parse_team_name(d.pop("teamName"))

        def _parse_server_slug(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        server_slug = _parse_server_slug(d.pop("serverSlug"))

        def _parse_profile_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        profile_name = _parse_profile_name(d.pop("profileName"))

        audit_log_response = cls(
            id=id,
            tenant_id=tenant_id,
            event_time=event_time,
            entity_type=entity_type,
            entity_id=entity_id,
            event_name=event_name,
            user_id=user_id,
            details=details,
            only_superadmin_visibility=only_superadmin_visibility,
            created_at=created_at,
            user_full_name=user_full_name,
            user_email=user_email,
            team_name=team_name,
            server_slug=server_slug,
            profile_name=profile_name,
        )

        return audit_log_response
