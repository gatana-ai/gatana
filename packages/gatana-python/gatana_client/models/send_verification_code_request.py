from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_300 import Schema300
from ..types import UNSET, Unset

T = TypeVar("T", bound="SendVerificationCodeRequest")


@_attrs_define
class SendVerificationCodeRequest:
    """
    Attributes:
        email (str):
        purpose (Schema300):
        turnstile_token (str | Unset):
        tenant_slug (str | Unset):
    """

    email: str
    purpose: Schema300
    turnstile_token: str | Unset = UNSET
    tenant_slug: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        purpose = self.purpose.value

        turnstile_token = self.turnstile_token

        tenant_slug = self.tenant_slug

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "purpose": purpose,
            }
        )
        if turnstile_token is not UNSET:
            field_dict["turnstileToken"] = turnstile_token
        if tenant_slug is not UNSET:
            field_dict["tenantSlug"] = tenant_slug

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        purpose = Schema300(d.pop("purpose"))

        turnstile_token = d.pop("turnstileToken", UNSET)

        tenant_slug = d.pop("tenantSlug", UNSET)

        send_verification_code_request = cls(
            email=email,
            purpose=purpose,
            turnstile_token=turnstile_token,
            tenant_slug=tenant_slug,
        )

        send_verification_code_request.additional_properties = d
        return send_verification_code_request

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
