from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema354")


@_attrs_define
class Schema354:
    """
    Attributes:
        cpu (str): CPU limit in Kubernetes quantity format (e.g. "500m" or "1")
        memory (str): Memory limit in Kubernetes quantity format (e.g. "512Mi" or "1Gi")
    """

    cpu: str
    memory: str

    def to_dict(self) -> dict[str, Any]:
        cpu = self.cpu

        memory = self.memory

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "cpu": cpu,
                "memory": memory,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cpu = d.pop("cpu")

        memory = d.pop("memory")

        schema_354 = cls(
            cpu=cpu,
            memory=memory,
        )

        return schema_354
