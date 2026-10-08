from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.scim_token import ScimToken


T = TypeVar("T", bound="GetScimTokensResponse")


@_attrs_define
class GetScimTokensResponse:
    """
    Attributes:
        tokens (list[ScimToken]): SCIM tokens of the organization
    """

    tokens: list[ScimToken]

    def to_dict(self) -> dict[str, Any]:
        tokens = []
        for componentsschemas_schema1054_item_data in self.tokens:
            componentsschemas_schema1054_item = componentsschemas_schema1054_item_data.to_dict()
            tokens.append(componentsschemas_schema1054_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tokens": tokens,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scim_token import ScimToken

        d = dict(src_dict)
        tokens = []
        _tokens = d.pop("tokens")
        for componentsschemas_schema1054_item_data in _tokens:
            componentsschemas_schema1054_item = ScimToken.from_dict(componentsschemas_schema1054_item_data)

            tokens.append(componentsschemas_schema1054_item)

        get_scim_tokens_response = cls(
            tokens=tokens,
        )

        return get_scim_tokens_response
