from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.server_pod_status import ServerPodStatus


T = TypeVar("T", bound="ServerRunningStatusResponse")


@_attrs_define
class ServerRunningStatusResponse:
    """
    Attributes:
        is_deployed (bool):
        is_available (bool):
        is_stabilizing (bool):
        pods (list[ServerPodStatus]):
    """

    is_deployed: bool
    is_available: bool
    is_stabilizing: bool
    pods: list[ServerPodStatus]

    def to_dict(self) -> dict[str, Any]:
        is_deployed = self.is_deployed

        is_available = self.is_available

        is_stabilizing = self.is_stabilizing

        pods = []
        for componentsschemas_schema598_item_data in self.pods:
            componentsschemas_schema598_item = componentsschemas_schema598_item_data.to_dict()
            pods.append(componentsschemas_schema598_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "isDeployed": is_deployed,
                "isAvailable": is_available,
                "isStabilizing": is_stabilizing,
                "pods": pods,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_pod_status import ServerPodStatus

        d = dict(src_dict)
        is_deployed = d.pop("isDeployed")

        is_available = d.pop("isAvailable")

        is_stabilizing = d.pop("isStabilizing")

        pods = []
        _pods = d.pop("pods")
        for componentsschemas_schema598_item_data in _pods:
            componentsschemas_schema598_item = ServerPodStatus.from_dict(componentsschemas_schema598_item_data)

            pods.append(componentsschemas_schema598_item)

        server_running_status_response = cls(
            is_deployed=is_deployed,
            is_available=is_available,
            is_stabilizing=is_stabilizing,
            pods=pods,
        )

        return server_running_status_response
