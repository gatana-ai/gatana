from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_status import DeploymentStatus
    from ..models.server_storage_status import ServerStorageStatus


T = TypeVar("T", bound="DeploymentStatusResponse")


@_attrs_define
class DeploymentStatusResponse:
    """
    Attributes:
        is_deployed (bool): Whether a deployment exists for the server or sandbox
        is_available (bool): Whether the deployment is available and serving
        is_stabilizing (bool): Whether the deployment is still rolling out or stabilizing
        deployments (list[DeploymentStatus]): Status of the pods of the deployment
        current_replica_set (str | Unset):
        storage (None | ServerStorageStatus | Unset):
    """

    is_deployed: bool
    is_available: bool
    is_stabilizing: bool
    deployments: list[DeploymentStatus]
    current_replica_set: str | Unset = UNSET
    storage: None | ServerStorageStatus | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.server_storage_status import ServerStorageStatus

        is_deployed = self.is_deployed

        is_available = self.is_available

        is_stabilizing = self.is_stabilizing

        deployments = []
        for componentsschemas_schema761_item_data in self.deployments:
            componentsschemas_schema761_item = componentsschemas_schema761_item_data.to_dict()
            deployments.append(componentsschemas_schema761_item)

        current_replica_set = self.current_replica_set

        storage: dict[str, Any] | None | Unset
        if isinstance(self.storage, Unset):
            storage = UNSET
        elif isinstance(self.storage, ServerStorageStatus):
            storage = self.storage.to_dict()
        else:
            storage = self.storage

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "isDeployed": is_deployed,
                "isAvailable": is_available,
                "isStabilizing": is_stabilizing,
                "deployments": deployments,
            }
        )
        if current_replica_set is not UNSET:
            field_dict["currentReplicaSet"] = current_replica_set
        if storage is not UNSET:
            field_dict["storage"] = storage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_status import DeploymentStatus
        from ..models.server_storage_status import ServerStorageStatus

        d = dict(src_dict)
        is_deployed = d.pop("isDeployed")

        is_available = d.pop("isAvailable")

        is_stabilizing = d.pop("isStabilizing")

        deployments = []
        _deployments = d.pop("deployments")
        for componentsschemas_schema761_item_data in _deployments:
            componentsschemas_schema761_item = DeploymentStatus.from_dict(componentsschemas_schema761_item_data)

            deployments.append(componentsschemas_schema761_item)

        current_replica_set = d.pop("currentReplicaSet", UNSET)

        def _parse_storage(data: object) -> None | ServerStorageStatus | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema788_type_0 = ServerStorageStatus.from_dict(data)

                return componentsschemas_schema788_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServerStorageStatus | Unset, data)

        storage = _parse_storage(d.pop("storage", UNSET))

        deployment_status_response = cls(
            is_deployed=is_deployed,
            is_available=is_available,
            is_stabilizing=is_stabilizing,
            deployments=deployments,
            current_replica_set=current_replica_set,
            storage=storage,
        )

        return deployment_status_response
