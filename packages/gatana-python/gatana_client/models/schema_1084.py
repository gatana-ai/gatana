from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_1074 import Schema1074

T = TypeVar("T", bound="Schema1084")


@_attrs_define
class Schema1084:
    """
    Attributes:
        client_id (str): OAuth client ID the connection authenticates as
        name (str): Best available display name for the client
        label (str): Name the user gave the connection; empty when unnamed
        client_info_name (str): Name the client reported over MCP; empty when it never reported one
        client_info_version (str): Version the client reported over MCP; empty when unknown
        kind (Schema1074): How the client registered itself, or external when it did not
        is_active (bool): Whether the connection can still be used: it holds a renewable refresh token, or for an
            external client, it made a request recently
        profile_ids (list[str]): Profiles the user attached to this connection
        first_seen_at (None | str): When the connection was first recorded; null before it authorizes or is used
        last_authorized_at (None | str): When the client last completed an authorization; null when not seen since
            recording began, and always null for an external client
        last_used_at (None | str): When the client last made a request; null when it has not made one
    """

    client_id: str
    name: str
    label: str
    client_info_name: str
    client_info_version: str
    kind: Schema1074
    is_active: bool
    profile_ids: list[str]
    first_seen_at: None | str
    last_authorized_at: None | str
    last_used_at: None | str

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        name = self.name

        label = self.label

        client_info_name = self.client_info_name

        client_info_version = self.client_info_version

        kind = self.kind.value

        is_active = self.is_active

        profile_ids = self.profile_ids

        first_seen_at: None | str
        first_seen_at = self.first_seen_at

        last_authorized_at: None | str
        last_authorized_at = self.last_authorized_at

        last_used_at: None | str
        last_used_at = self.last_used_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "clientId": client_id,
                "name": name,
                "label": label,
                "clientInfoName": client_info_name,
                "clientInfoVersion": client_info_version,
                "kind": kind,
                "isActive": is_active,
                "profileIds": profile_ids,
                "firstSeenAt": first_seen_at,
                "lastAuthorizedAt": last_authorized_at,
                "lastUsedAt": last_used_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_id = d.pop("clientId")

        name = d.pop("name")

        label = d.pop("label")

        client_info_name = d.pop("clientInfoName")

        client_info_version = d.pop("clientInfoVersion")

        kind = Schema1074(d.pop("kind"))

        is_active = d.pop("isActive")

        profile_ids = cast(list[str], d.pop("profileIds"))

        def _parse_first_seen_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        first_seen_at = _parse_first_seen_at(d.pop("firstSeenAt"))

        def _parse_last_authorized_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_authorized_at = _parse_last_authorized_at(d.pop("lastAuthorizedAt"))

        def _parse_last_used_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_used_at = _parse_last_used_at(d.pop("lastUsedAt"))

        schema_1084 = cls(
            client_id=client_id,
            name=name,
            label=label,
            client_info_name=client_info_name,
            client_info_version=client_info_version,
            kind=kind,
            is_active=is_active,
            profile_ids=profile_ids,
            first_seen_at=first_seen_at,
            last_authorized_at=last_authorized_at,
            last_used_at=last_used_at,
        )

        return schema_1084
