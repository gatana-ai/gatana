from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema503")


@_attrs_define
class Schema503:
    """
    Attributes:
        type_ (Literal['self']): Transport type discriminator, always "self"
        id (str): ID of the built-in server implementation
    """

    type_: Literal["self"]
    id: str

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        id = self.id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["self"], d.pop("type"))
        if type_ != "self":
            raise ValueError(f"type must match const 'self', got '{type_}'")

        id = d.pop("id")

        schema_503 = cls(
            type_=type_,
            id=id,
        )

        return schema_503
