from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema107")


@_attrs_define
class Schema107:
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
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cpu = self.cpu

        memory = self.memory

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
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

        schema_107 = cls(
            cpu=cpu,
            memory=memory,
        )

        schema_107.additional_properties = d
        return schema_107

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
