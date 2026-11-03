from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="SendVerificationCodeResponse")


@_attrs_define
class SendVerificationCodeResponse:
    """
    Attributes:
        success (bool):
        verification_required (bool):
    """

    success: bool
    verification_required: bool

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        verification_required = self.verification_required

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "success": success,
                "verificationRequired": verification_required,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        verification_required = d.pop("verificationRequired")

        send_verification_code_response = cls(
            success=success,
            verification_required=verification_required,
        )

        return send_verification_code_response
