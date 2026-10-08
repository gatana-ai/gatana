from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_15 import Schema15

T = TypeVar("T", bound="CreateUserRequest")


@_attrs_define
class CreateUserRequest:
    """
    Attributes:
        email (str): Email address of the new user
        name (str): Display name of the new user
        role (Schema15):
        is_service_account (bool): Whether to create a service account instead of a regular user
    """

    email: str
    name: str
    role: Schema15
    is_service_account: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        role = self.role.value

        is_service_account = self.is_service_account

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "name": name,
                "role": role,
                "isServiceAccount": is_service_account,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        name = d.pop("name")

        role = Schema15(d.pop("role"))

        is_service_account = d.pop("isServiceAccount")

        create_user_request = cls(
            email=email,
            name=name,
            role=role,
            is_service_account=is_service_account,
        )

        create_user_request.additional_properties = d
        return create_user_request

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
