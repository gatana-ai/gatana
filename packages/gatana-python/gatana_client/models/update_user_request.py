from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_23 import Schema23
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateUserRequest")


@_attrs_define
class UpdateUserRequest:
    """
    Attributes:
        email (str | Unset):
        name (str | Unset):
        role (Schema23 | Unset):
        is_disabled (bool | Unset):
        is_scim_managed (bool | Unset):
        scim_external_id (str | Unset):
    """

    email: str | Unset = UNSET
    name: str | Unset = UNSET
    role: Schema23 | Unset = UNSET
    is_disabled: bool | Unset = UNSET
    is_scim_managed: bool | Unset = UNSET
    scim_external_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        role: str | Unset = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        is_disabled = self.is_disabled

        is_scim_managed = self.is_scim_managed

        scim_external_id = self.scim_external_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if name is not UNSET:
            field_dict["name"] = name
        if role is not UNSET:
            field_dict["role"] = role
        if is_disabled is not UNSET:
            field_dict["isDisabled"] = is_disabled
        if is_scim_managed is not UNSET:
            field_dict["isScimManaged"] = is_scim_managed
        if scim_external_id is not UNSET:
            field_dict["scimExternalId"] = scim_external_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        name = d.pop("name", UNSET)

        _role = d.pop("role", UNSET)
        role: Schema23 | Unset
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = Schema23(_role)

        is_disabled = d.pop("isDisabled", UNSET)

        is_scim_managed = d.pop("isScimManaged", UNSET)

        scim_external_id = d.pop("scimExternalId", UNSET)

        update_user_request = cls(
            email=email,
            name=name,
            role=role,
            is_disabled=is_disabled,
            is_scim_managed=is_scim_managed,
            scim_external_id=scim_external_id,
        )

        update_user_request.additional_properties = d
        return update_user_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
