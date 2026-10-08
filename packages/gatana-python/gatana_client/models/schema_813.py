from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema813")


@_attrs_define
class Schema813:
    """
    Attributes:
        type_ (Literal['error']): Event type discriminator, always "error"
        message (str): Error message
    """

    type_: Literal["error"]
    message: str

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        message = self.message

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["error"], d.pop("type"))
        if type_ != "error":
            raise ValueError(f"type must match const 'error', got '{type_}'")

        message = d.pop("message")

        schema_813 = cls(
            type_=type_,
            message=message,
        )

        return schema_813
