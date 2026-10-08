from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema805")


@_attrs_define
class Schema805:
    """
    Attributes:
        cpu_cores (float | None): CPU reserved for the deployment in cores (its guaranteed minimum under load), or null
        memory_bytes (float | None): Memory reserved for the deployment in bytes (also its hard ceiling), or null
    """

    cpu_cores: float | None
    memory_bytes: float | None

    def to_dict(self) -> dict[str, Any]:
        cpu_cores: float | None
        cpu_cores = self.cpu_cores

        memory_bytes: float | None
        memory_bytes = self.memory_bytes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "cpuCores": cpu_cores,
                "memoryBytes": memory_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_cpu_cores(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        cpu_cores = _parse_cpu_cores(d.pop("cpuCores"))

        def _parse_memory_bytes(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        memory_bytes = _parse_memory_bytes(d.pop("memoryBytes"))

        schema_805 = cls(
            cpu_cores=cpu_cores,
            memory_bytes=memory_bytes,
        )

        return schema_805
