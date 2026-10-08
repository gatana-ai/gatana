from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ServerResourceRequests")


@_attrs_define
class ServerResourceRequests:
    """
    Attributes:
        cpu (str): CPU reserved for the deployment, in Kubernetes quantity format (e.g. "250m" or "1"). This is the
            minimum the deployment is guaranteed when the hardware is busy; when capacity is free it may use more. Reserved
            capacity counts against the organization total even while the server idles, so keep it at what the server needs,
            not what it may burst to
        memory (str): Memory reserved for the deployment, in Kubernetes quantity format (e.g. "384Mi" or "1Gi"). Unlike
            CPU this is also the hard ceiling: a process that exceeds it is terminated
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

        server_resource_requests = cls(
            cpu=cpu,
            memory=memory,
        )

        return server_resource_requests
