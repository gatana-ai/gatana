from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateUserMeRequest")


@_attrs_define
class UpdateUserMeRequest:
    """
    Attributes:
        email (str | Unset):
        name (str | Unset):
        password (str | Unset):
        email_verification_code (str | Unset):
    """

    email: str | Unset = UNSET
    name: str | Unset = UNSET
    password: str | Unset = UNSET
    email_verification_code: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        password = self.password

        email_verification_code = self.email_verification_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if name is not UNSET:
            field_dict["name"] = name
        if password is not UNSET:
            field_dict["password"] = password
        if email_verification_code is not UNSET:
            field_dict["emailVerificationCode"] = email_verification_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        name = d.pop("name", UNSET)

        password = d.pop("password", UNSET)

        email_verification_code = d.pop("emailVerificationCode", UNSET)

        update_user_me_request = cls(
            email=email,
            name=name,
            password=password,
            email_verification_code=email_verification_code,
        )

        update_user_me_request.additional_properties = d
        return update_user_me_request

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
