from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.personal_access_token import PersonalAccessToken


T = TypeVar("T", bound="Schema496")


@_attrs_define
class Schema496:
    """
    Attributes:
        tokens (list[PersonalAccessToken]): Personal access tokens of the user
    """

    tokens: list[PersonalAccessToken]

    def to_dict(self) -> dict[str, Any]:
        tokens = []
        for tokens_item_data in self.tokens:
            tokens_item = tokens_item_data.to_dict()
            tokens.append(tokens_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tokens": tokens,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.personal_access_token import PersonalAccessToken

        d = dict(src_dict)
        tokens = []
        _tokens = d.pop("tokens")
        for tokens_item_data in _tokens:
            tokens_item = PersonalAccessToken.from_dict(tokens_item_data)

            tokens.append(tokens_item)

        schema_496 = cls(
            tokens=tokens,
        )

        return schema_496
