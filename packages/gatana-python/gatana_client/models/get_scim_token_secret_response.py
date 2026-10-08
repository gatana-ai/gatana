from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetScimTokenSecretResponse")


@_attrs_define
class GetScimTokenSecretResponse:
    """
    Attributes:
        raw_token (str): Raw token secret
    """

    raw_token: str

    def to_dict(self) -> dict[str, Any]:
        raw_token = self.raw_token

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "rawToken": raw_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        raw_token = d.pop("rawToken")

        get_scim_token_secret_response = cls(
            raw_token=raw_token,
        )

        return get_scim_token_secret_response
