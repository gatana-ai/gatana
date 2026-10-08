from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema851")


@_attrs_define
class Schema851:
    """
    Attributes:
        type_ (Literal['initContainerTerminated']): Event type discriminator, always "initContainerTerminated"
        name (str): Name of the init container
        exit_code (float): Exit code of the init container
        started_at (str): Time when the container started
        finished_at (str): Time when the container terminated
        reason (str | Unset):
    """

    type_: Literal["initContainerTerminated"]
    name: str
    exit_code: float
    started_at: str
    finished_at: str
    reason: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        name = self.name

        exit_code = self.exit_code

        started_at = self.started_at

        finished_at = self.finished_at

        reason = self.reason

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "name": name,
                "exitCode": exit_code,
                "startedAt": started_at,
                "finishedAt": finished_at,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["initContainerTerminated"], d.pop("type"))
        if type_ != "initContainerTerminated":
            raise ValueError(f"type must match const 'initContainerTerminated', got '{type_}'")

        name = d.pop("name")

        exit_code = d.pop("exitCode")

        started_at = d.pop("startedAt")

        finished_at = d.pop("finishedAt")

        reason = d.pop("reason", UNSET)

        schema_851 = cls(
            type_=type_,
            name=name,
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            reason=reason,
        )

        return schema_851
