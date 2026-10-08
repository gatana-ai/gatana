from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema853")


@_attrs_define
class Schema853:
    """
    Attributes:
        type_ (Literal['sidecarContainerStarted']): Event type discriminator, always "sidecarContainerStarted"
        name (str): Name of the sidecar container
        started_at (str): Time when the container started
    """

    type_: Literal["sidecarContainerStarted"]
    name: str
    started_at: str

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        name = self.name

        started_at = self.started_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "name": name,
                "startedAt": started_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["sidecarContainerStarted"], d.pop("type"))
        if type_ != "sidecarContainerStarted":
            raise ValueError(f"type must match const 'sidecarContainerStarted', got '{type_}'")

        name = d.pop("name")

        started_at = d.pop("startedAt")

        schema_853 = cls(
            type_=type_,
            name=name,
            started_at=started_at,
        )

        return schema_853
