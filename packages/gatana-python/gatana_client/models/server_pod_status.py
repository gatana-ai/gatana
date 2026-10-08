from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="ServerPodStatus")



@_attrs_define
class ServerPodStatus:
    """ 
        Attributes:
            name (str):
            ready (bool):
            phase (str | Unset):
            reason (str | Unset):
            created_at (str | Unset):
     """

    name: str
    ready: bool
    phase: str | Unset = UNSET
    reason: str | Unset = UNSET
    created_at: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        ready = self.ready

        phase = self.phase

        reason = self.reason

        created_at = self.created_at


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "name": name,
            "ready": ready,
        })
        if phase is not UNSET:
            field_dict["phase"] = phase
        if reason is not UNSET:
            field_dict["reason"] = reason
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        ready = d.pop("ready")

        phase = d.pop("phase", UNSET)

        reason = d.pop("reason", UNSET)

        created_at = d.pop("createdAt", UNSET)

        server_pod_status = cls(
            name=name,
            ready=ready,
            phase=phase,
            reason=reason,
            created_at=created_at,
        )

        return server_pod_status

