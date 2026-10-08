from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_826 import Schema826
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentContainerStatus")


@_attrs_define
class DeploymentContainerStatus:
    """
    Attributes:
        name (str): Name of the container
        status (Schema826): State of the container right now
        restarts (float): Number of times the container has restarted
        started_at (str | Unset):
        finished_at (str | Unset):
        exit_code (float | Unset):
        reason (str | Unset):
    """

    name: str
    status: Schema826
    restarts: float
    started_at: str | Unset = UNSET
    finished_at: str | Unset = UNSET
    exit_code: float | Unset = UNSET
    reason: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        status = self.status.value

        restarts = self.restarts

        started_at = self.started_at

        finished_at = self.finished_at

        exit_code = self.exit_code

        reason = self.reason

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "status": status,
                "restarts": restarts,
            }
        )
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if finished_at is not UNSET:
            field_dict["finishedAt"] = finished_at
        if exit_code is not UNSET:
            field_dict["exitCode"] = exit_code
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        status = Schema826(d.pop("status"))

        restarts = d.pop("restarts")

        started_at = d.pop("startedAt", UNSET)

        finished_at = d.pop("finishedAt", UNSET)

        exit_code = d.pop("exitCode", UNSET)

        reason = d.pop("reason", UNSET)

        deployment_container_status = cls(
            name=name,
            status=status,
            restarts=restarts,
            started_at=started_at,
            finished_at=finished_at,
            exit_code=exit_code,
            reason=reason,
        )

        return deployment_container_status
