from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="SiemSigningSecretResponse")


@_attrs_define
class SiemSigningSecretResponse:
    """
    Attributes:
        signing_secret (str): Secret used to compute the HMAC signature of delivered batches
    """

    signing_secret: str

    def to_dict(self) -> dict[str, Any]:
        signing_secret = self.signing_secret

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "signingSecret": signing_secret,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        signing_secret = d.pop("signingSecret")

        siem_signing_secret_response = cls(
            signing_secret=signing_secret,
        )

        return siem_signing_secret_response
