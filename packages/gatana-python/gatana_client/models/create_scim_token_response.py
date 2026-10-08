from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1065 import Schema1065


T = TypeVar("T", bound="CreateScimTokenResponse")


@_attrs_define
class CreateScimTokenResponse:
    """
    Attributes:
        token (Schema1065):
        raw_token (str): Raw token secret to configure in the identity provider
    """

    token: Schema1065
    raw_token: str

    def to_dict(self) -> dict[str, Any]:
        token = self.token.to_dict()

        raw_token = self.raw_token

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "token": token,
                "rawToken": raw_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1065 import Schema1065

        d = dict(src_dict)
        token = Schema1065.from_dict(d.pop("token"))

        raw_token = d.pop("rawToken")

        create_scim_token_response = cls(
            token=token,
            raw_token=raw_token,
        )

        return create_scim_token_response
