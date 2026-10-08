from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_815 import Schema815
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_container_status import DeploymentContainerStatus
    from ..models.schema_774 import Schema774
    from ..models.schema_843 import Schema843
    from ..models.schema_845 import Schema845


T = TypeVar("T", bound="DeploymentLogPayloadPodInfo")


@_attrs_define
class DeploymentLogPayloadPodInfo:
    """
    Attributes:
        type_ (Literal['podInfo']): Event type discriminator, always "podInfo"
        status (Schema815): Status of the pod
        created_at (str): Time when the pod was created
        pod (str): Name of the pod
        init_containers (list[str]): Names of the init containers
        sidecar_containers (list[str]): Names of the init containers that are sidecars, and so keep running beside the
            server instead of terminating
        readable_containers (list[str]): Names of the containers whose logs can be read. The platform own init
            containers are not among them
        container_statuses (list[DeploymentContainerStatus]): State of every container of the pod when the stream
            opened, so that a pod which is past its transitions still reports what it is doing
        containers (list[str]): Names of the containers
        waiting_reason (None | str): Reason a container is waiting, or null
        restart_count (float): Number of container restarts
        has_previous_failure (bool): Whether a previous container instance failed
        last_fail_condition (None | Schema774): Pod condition of the last failure, or null
        is_sandbox (bool): Whether the pod belongs to a sandbox
        resource_limits (Schema845): Resources reserved for the pod
        last_failure (Schema843 | Unset):
    """

    type_: Literal["podInfo"]
    status: Schema815
    created_at: str
    pod: str
    init_containers: list[str]
    sidecar_containers: list[str]
    readable_containers: list[str]
    container_statuses: list[DeploymentContainerStatus]
    containers: list[str]
    waiting_reason: None | str
    restart_count: float
    has_previous_failure: bool
    last_fail_condition: None | Schema774
    is_sandbox: bool
    resource_limits: Schema845
    last_failure: Schema843 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_774 import Schema774

        type_ = self.type_

        status = self.status.value

        created_at = self.created_at

        pod = self.pod

        init_containers = self.init_containers

        sidecar_containers = self.sidecar_containers

        readable_containers = self.readable_containers

        container_statuses = []
        for componentsschemas_schema824_item_data in self.container_statuses:
            componentsschemas_schema824_item = componentsschemas_schema824_item_data.to_dict()
            container_statuses.append(componentsschemas_schema824_item)

        containers = self.containers

        waiting_reason: None | str
        waiting_reason = self.waiting_reason

        restart_count = self.restart_count

        has_previous_failure = self.has_previous_failure

        last_fail_condition: dict[str, Any] | None
        if isinstance(self.last_fail_condition, Schema774):
            last_fail_condition = self.last_fail_condition.to_dict()
        else:
            last_fail_condition = self.last_fail_condition

        is_sandbox = self.is_sandbox

        resource_limits = self.resource_limits.to_dict()

        last_failure: dict[str, Any] | Unset = UNSET
        if not isinstance(self.last_failure, Unset):
            last_failure = self.last_failure.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "status": status,
                "createdAt": created_at,
                "pod": pod,
                "initContainers": init_containers,
                "sidecarContainers": sidecar_containers,
                "readableContainers": readable_containers,
                "containerStatuses": container_statuses,
                "containers": containers,
                "waitingReason": waiting_reason,
                "restartCount": restart_count,
                "hasPreviousFailure": has_previous_failure,
                "lastFailCondition": last_fail_condition,
                "isSandbox": is_sandbox,
                "resourceLimits": resource_limits,
            }
        )
        if last_failure is not UNSET:
            field_dict["lastFailure"] = last_failure

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_container_status import DeploymentContainerStatus
        from ..models.schema_774 import Schema774
        from ..models.schema_843 import Schema843
        from ..models.schema_845 import Schema845

        d = dict(src_dict)
        type_ = cast(Literal["podInfo"], d.pop("type"))
        if type_ != "podInfo":
            raise ValueError(f"type must match const 'podInfo', got '{type_}'")

        status = Schema815(d.pop("status"))

        created_at = d.pop("createdAt")

        pod = d.pop("pod")

        init_containers = cast(list[str], d.pop("initContainers"))

        sidecar_containers = cast(list[str], d.pop("sidecarContainers"))

        readable_containers = cast(list[str], d.pop("readableContainers"))

        container_statuses = []
        _container_statuses = d.pop("containerStatuses")
        for componentsschemas_schema824_item_data in _container_statuses:
            componentsschemas_schema824_item = DeploymentContainerStatus.from_dict(
                componentsschemas_schema824_item_data
            )

            container_statuses.append(componentsschemas_schema824_item)

        containers = cast(list[str], d.pop("containers"))

        def _parse_waiting_reason(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        waiting_reason = _parse_waiting_reason(d.pop("waitingReason"))

        restart_count = d.pop("restartCount")

        has_previous_failure = d.pop("hasPreviousFailure")

        def _parse_last_fail_condition(data: object) -> None | Schema774:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema842_type_0 = Schema774.from_dict(data)

                return componentsschemas_schema842_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema774, data)

        last_fail_condition = _parse_last_fail_condition(d.pop("lastFailCondition"))

        is_sandbox = d.pop("isSandbox")

        resource_limits = Schema845.from_dict(d.pop("resourceLimits"))

        _last_failure = d.pop("lastFailure", UNSET)
        last_failure: Schema843 | Unset
        if isinstance(_last_failure, Unset):
            last_failure = UNSET
        else:
            last_failure = Schema843.from_dict(_last_failure)

        deployment_log_payload_pod_info = cls(
            type_=type_,
            status=status,
            created_at=created_at,
            pod=pod,
            init_containers=init_containers,
            sidecar_containers=sidecar_containers,
            readable_containers=readable_containers,
            container_statuses=container_statuses,
            containers=containers,
            waiting_reason=waiting_reason,
            restart_count=restart_count,
            has_previous_failure=has_previous_failure,
            last_fail_condition=last_fail_condition,
            is_sandbox=is_sandbox,
            resource_limits=resource_limits,
            last_failure=last_failure,
        )

        return deployment_log_payload_pod_info
