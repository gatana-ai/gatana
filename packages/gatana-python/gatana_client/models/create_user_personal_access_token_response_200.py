from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.personal_access_token import PersonalAccessToken


T = TypeVar("T", bound="CreateUserPersonalAccessTokenResponse200")


@_attrs_define
class CreateUserPersonalAccessTokenResponse200:
    """
    Attributes:
        token (PersonalAccessToken):
    """

    token: PersonalAccessToken

    def to_dict(self) -> dict[str, Any]:
        token = self.token.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "token": token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.personal_access_token import PersonalAccessToken

        d = dict(src_dict)
        token = PersonalAccessToken.from_dict(d.pop("token"))

        create_user_personal_access_token_response_200 = cls(
            token=token,
        )

        return create_user_personal_access_token_response_200
