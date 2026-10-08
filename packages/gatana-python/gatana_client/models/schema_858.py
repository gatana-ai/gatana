from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema858")


@_attrs_define
class Schema858:
    """
    Attributes:
        type_ (Literal['mainContainerWaiting']): Event type discriminator, always "mainContainerWaiting"
        reason (str): Reason the main container is waiting
    """

    type_: Literal["mainContainerWaiting"]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        reason = self.reason

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["mainContainerWaiting"], d.pop("type"))
        if type_ != "mainContainerWaiting":
            raise ValueError(f"type must match const 'mainContainerWaiting', got '{type_}'")

        reason = d.pop("reason")

        schema_858 = cls(
            type_=type_,
            reason=reason,
        )

        return schema_858
