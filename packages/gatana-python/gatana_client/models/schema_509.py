from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema509")


@_attrs_define
class Schema509:
    """
    Attributes:
        cpu (str | Unset): CPU limit in Kubernetes quantity format (e.g. "500m" or "1")
        memory (str | Unset): Memory limit in Kubernetes quantity format (e.g. "512Mi" or "1Gi")
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

        schema_509 = cls(
            cpu=cpu,
            memory=memory,
        )

        return schema_509
