from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema864")


@_attrs_define
class Schema864:
    """
    Attributes:
        type_ (Literal['mainContainerReady']): Event type discriminator, always "mainContainerReady"
    """

    type_: Literal["mainContainerReady"]

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["mainContainerReady"], d.pop("type"))
        if type_ != "mainContainerReady":
            raise ValueError(f"type must match const 'mainContainerReady', got '{type_}'")

        schema_864 = cls(
            type_=type_,
        )

        return schema_864
