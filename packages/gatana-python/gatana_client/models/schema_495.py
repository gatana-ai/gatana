from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema495")


@_attrs_define
class Schema495:
    """
    Attributes:
        cpu (str | Unset): CPU reserved for the deployment, in Kubernetes quantity format (e.g. "250m" or "1"). This is
            the minimum the deployment is guaranteed when the hardware is busy; when capacity is free it may use more.
            Reserved capacity counts against the organization total even while the server idles, so keep it at what the
            server needs, not what it may burst to
        memory (str | Unset): Memory reserved for the deployment, in Kubernetes quantity format (e.g. "384Mi" or "1Gi").
            Unlike CPU this is also the hard ceiling: a process that exceeds it is terminated
    """

    cpu: str | Unset = UNSET
    memory: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        cpu = self.cpu

        memory = self.memory

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if cpu is not UNSET:
            field_dict["cpu"] = cpu
        if memory is not UNSET:
            field_dict["memory"] = memory

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cpu = d.pop("cpu", UNSET)

        memory = d.pop("memory", UNSET)

        schema_495 = cls(
            cpu=cpu,
            memory=memory,
        )

        return schema_495
