from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema780")


@_attrs_define
class Schema780:
    """
    Attributes:
        container_name (str): Name of the failed container
        exit_code (float | Unset):
        reason (str | Unset):
        message (str | Unset):
        finished_at (str | Unset):
    """

    container_name: str
    exit_code: float | Unset = UNSET
    reason: str | Unset = UNSET
    message: str | Unset = UNSET
    finished_at: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        container_name = self.container_name

        exit_code = self.exit_code

        reason = self.reason

        message = self.message

        finished_at = self.finished_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "containerName": container_name,
            }
        )
        if exit_code is not UNSET:
            field_dict["exitCode"] = exit_code
        if reason is not UNSET:
            field_dict["reason"] = reason
        if message is not UNSET:
            field_dict["message"] = message
        if finished_at is not UNSET:
            field_dict["finishedAt"] = finished_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        container_name = d.pop("containerName")

        exit_code = d.pop("exitCode", UNSET)

        reason = d.pop("reason", UNSET)

        message = d.pop("message", UNSET)

        finished_at = d.pop("finishedAt", UNSET)

        schema_780 = cls(
            container_name=container_name,
            exit_code=exit_code,
            reason=reason,
            message=message,
            finished_at=finished_at,
        )

        return schema_780
