from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_423 import Schema423

if TYPE_CHECKING:
    from ..models.profile_assignment import ProfileAssignment


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        id (str): Unique ID of the user
        tenant_id (str): ID of the tenant that owns the user
        name (str): Display name of the user
        email (str): Email address of the user
        role (Schema423):
        is_super_administrator (bool): Whether the user is a super administrator
        is_disabled (bool): Whether the user is disabled
        is_service_account (bool): Whether the user is a service account
        is_invited (bool): Whether the user was invited and has not set a password yet
        profile_ids (list[ProfileAssignment]): Profile assignments of the user
        is_scim_managed (bool): Whether the user is managed through SCIM provisioning
        scim_external_id (str): SCIM external ID of the user
        created_at (str): Time when the user was created
        updated_at (str): Time when the user was last updated
    """

    id: str
    tenant_id: str
    name: str
    email: str
    role: Schema423
    is_super_administrator: bool
    is_disabled: bool
    is_service_account: bool
    is_invited: bool
    profile_ids: list[ProfileAssignment]
    is_scim_managed: bool
    scim_external_id: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        name = self.name

        email = self.email

        role = self.role.value

        is_super_administrator = self.is_super_administrator

        is_disabled = self.is_disabled

        is_service_account = self.is_service_account

        is_invited = self.is_invited

        profile_ids = []
        for componentsschemas_schema427_item_data in self.profile_ids:
            componentsschemas_schema427_item = componentsschemas_schema427_item_data.to_dict()
            profile_ids.append(componentsschemas_schema427_item)

        is_scim_managed = self.is_scim_managed

        scim_external_id = self.scim_external_id

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "name": name,
                "email": email,
                "role": role,
                "isSuperAdministrator": is_super_administrator,
                "isDisabled": is_disabled,
                "isServiceAccount": is_service_account,
                "isInvited": is_invited,
                "profileIds": profile_ids,
                "isScimManaged": is_scim_managed,
                "scimExternalId": scim_external_id,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_assignment import ProfileAssignment

        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        name = d.pop("name")

        email = d.pop("email")

        role = Schema423(d.pop("role"))

        is_super_administrator = d.pop("isSuperAdministrator")

        is_disabled = d.pop("isDisabled")

        is_service_account = d.pop("isServiceAccount")

        is_invited = d.pop("isInvited")

        profile_ids = []
        _profile_ids = d.pop("profileIds")
        for componentsschemas_schema427_item_data in _profile_ids:
            componentsschemas_schema427_item = ProfileAssignment.from_dict(componentsschemas_schema427_item_data)

            profile_ids.append(componentsschemas_schema427_item)

        is_scim_managed = d.pop("isScimManaged")

        scim_external_id = d.pop("scimExternalId")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        user = cls(
            id=id,
            tenant_id=tenant_id,
            name=name,
            email=email,
            role=role,
            is_super_administrator=is_super_administrator,
            is_disabled=is_disabled,
            is_service_account=is_service_account,
            is_invited=is_invited,
            profile_ids=profile_ids,
            is_scim_managed=is_scim_managed,
            scim_external_id=scim_external_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        return user
