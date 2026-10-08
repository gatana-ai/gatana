from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema854")


@_attrs_define
class Schema854:
    """
    Attributes:
        type_ (Literal['sidecarContainerFailed']): Event type discriminator, always "sidecarContainerFailed"
        name (str): Name of the sidecar container
        restarts (float): Number of times the container has restarted
        is_backing_off (bool): Whether the kubelet is holding the container off before another attempt
        exit_code (float | Unset):
        reason (str | Unset):
        message (str | Unset):
    """

    type_: Literal["sidecarContainerFailed"]
    name: str
    restarts: float
    is_backing_off: bool
    exit_code: float | Unset = UNSET
    reason: str | Unset = UNSET
    message: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        name = self.name

        restarts = self.restarts

        is_backing_off = self.is_backing_off

        exit_code = self.exit_code

        reason = self.reason

        message = self.message

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "name": name,
                "restarts": restarts,
                "isBackingOff": is_backing_off,
            }
        )
        if exit_code is not UNSET:
            field_dict["exitCode"] = exit_code
        if reason is not UNSET:
            field_dict["reason"] = reason
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["sidecarContainerFailed"], d.pop("type"))
        if type_ != "sidecarContainerFailed":
            raise ValueError(f"type must match const 'sidecarContainerFailed', got '{type_}'")

        name = d.pop("name")

        restarts = d.pop("restarts")

        is_backing_off = d.pop("isBackingOff")

        exit_code = d.pop("exitCode", UNSET)

        reason = d.pop("reason", UNSET)

        message = d.pop("message", UNSET)

        schema_854 = cls(
            type_=type_,
            name=name,
            restarts=restarts,
            is_backing_off=is_backing_off,
            exit_code=exit_code,
            reason=reason,
            message=message,
        )

        return schema_854
