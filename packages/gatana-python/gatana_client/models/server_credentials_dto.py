from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_632 import Schema632
from ..models.schema_641 import Schema641

T = TypeVar("T", bound="ServerCredentialsDto")


@_attrs_define
class ServerCredentialsDto:
    """
    Attributes:
        id (str): Unique ID of the credential record
        tenant_id (str): ID of the tenant that owns the credential
        scope (Schema632):
        user_id (None | str): ID of the owning user, or null
        profile_id (None | str): ID of the owning profile when scope is "profile", otherwise null
        last_used_at (None | str): Time when the credential was last used, or null if never used
        authorized_at (str): Time when the credential was authorized
        type_ (Schema641): Authorization method that the credential was created with
        created_at (str): Time when the credential record was created
        updated_at (str): Time when the credential record was last updated
        server_slug (str): Slug of the server that the credential authorizes access to
        user_email (None | str): Email address of the owning user, or null
        user_name (None | str): Display name of the owning user, or null
        profile_name (None | str): Name of the owning profile, or null
        apikeys_present (list[str] | None): Names of the API keys that have a stored value, or null for OAuth
            credentials
        subject (None | str): Subject claim from the OAuth ID token, or null
        email (None | str): Email claim from the OAuth ID token, or null
    """

    id: str
    tenant_id: str
    scope: Schema632
    user_id: None | str
    profile_id: None | str
    last_used_at: None | str
    authorized_at: str
    type_: Schema641
    created_at: str
    updated_at: str
    server_slug: str
    user_email: None | str
    user_name: None | str
    profile_name: None | str
    apikeys_present: list[str] | None
    subject: None | str
    email: None | str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        scope = self.scope.value

        user_id: None | str
        user_id = self.user_id

        profile_id: None | str
        profile_id = self.profile_id

        last_used_at: None | str
        last_used_at = self.last_used_at

        authorized_at = self.authorized_at

        type_ = self.type_.value

        created_at = self.created_at

        updated_at = self.updated_at

        server_slug = self.server_slug

        user_email: None | str
        user_email = self.user_email

        user_name: None | str
        user_name = self.user_name

        profile_name: None | str
        profile_name = self.profile_name

        apikeys_present: list[str] | None
        if isinstance(self.apikeys_present, list):
            apikeys_present = self.apikeys_present

        else:
            apikeys_present = self.apikeys_present

        subject: None | str
        subject = self.subject

        email: None | str
        email = self.email

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "scope": scope,
                "userId": user_id,
                "profileId": profile_id,
                "lastUsedAt": last_used_at,
                "authorizedAt": authorized_at,
                "type": type_,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "serverSlug": server_slug,
                "userEmail": user_email,
                "userName": user_name,
                "profileName": profile_name,
                "apikeysPresent": apikeys_present,
                "subject": subject,
                "email": email,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        scope = Schema632(d.pop("scope"))

        def _parse_user_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        user_id = _parse_user_id(d.pop("userId"))

        def _parse_profile_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        profile_id = _parse_profile_id(d.pop("profileId"))

        def _parse_last_used_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_used_at = _parse_last_used_at(d.pop("lastUsedAt"))

        authorized_at = d.pop("authorizedAt")

        type_ = Schema641(d.pop("type"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        server_slug = d.pop("serverSlug")

        def _parse_user_email(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        user_email = _parse_user_email(d.pop("userEmail"))

        def _parse_user_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        user_name = _parse_user_name(d.pop("userName"))

        def _parse_profile_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        profile_name = _parse_profile_name(d.pop("profileName"))

        def _parse_apikeys_present(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemas_schema651_type_0 = cast(list[str], data)

                return componentsschemas_schema651_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None, data)

        apikeys_present = _parse_apikeys_present(d.pop("apikeysPresent"))

        def _parse_subject(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        subject = _parse_subject(d.pop("subject"))

        def _parse_email(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        email = _parse_email(d.pop("email"))

        server_credentials_dto = cls(
            id=id,
            tenant_id=tenant_id,
            scope=scope,
            user_id=user_id,
            profile_id=profile_id,
            last_used_at=last_used_at,
            authorized_at=authorized_at,
            type_=type_,
            created_at=created_at,
            updated_at=updated_at,
            server_slug=server_slug,
            user_email=user_email,
            user_name=user_name,
            profile_name=profile_name,
            apikeys_present=apikeys_present,
            subject=subject,
            email=email,
        )

        return server_credentials_dto
