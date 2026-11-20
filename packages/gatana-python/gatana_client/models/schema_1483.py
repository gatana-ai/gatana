from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema1483")


@_attrs_define
class Schema1483:
    """
    Attributes:
        message (str):
        authorize_url (None | str): Link that stores the credential. null when the caller cannot set it
    """

    message: str
    authorize_url: None | str

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        authorize_url: None | str
        authorize_url = self.authorize_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "message": message,
                "authorizeUrl": authorize_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message")

        def _parse_authorize_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        authorize_url = _parse_authorize_url(d.pop("authorizeUrl"))

        schema_1483 = cls(
            message=message,
            authorize_url=authorize_url,
        )

        return schema_1483
