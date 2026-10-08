from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_774 import Schema774
    from ..models.schema_780 import Schema780


T = TypeVar("T", bound="DeploymentStatus")


@_attrs_define
class DeploymentStatus:
    """
    Attributes:
        name (str): Name of the pod
        ready (bool): Whether all containers of the pod are ready
        crash (bool): Whether a container is crash-looping or terminated with an error
        restart_count (float): Number of container restarts
        has_previous_failure (bool): Whether a previous container instance failed
        last_fail_condition (None | Schema774): Pod condition of the last failure, or null
        phase (str | Unset):
        reason (str | Unset):
        created_at (str | Unset):
        last_failure (Schema780 | Unset):
        waiting_reason (str | Unset):
    """

    name: str
    ready: bool
    crash: bool
    restart_count: float
    has_previous_failure: bool
    last_fail_condition: None | Schema774
    phase: str | Unset = UNSET
    reason: str | Unset = UNSET
    created_at: str | Unset = UNSET
    last_failure: Schema780 | Unset = UNSET
    waiting_reason: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_774 import Schema774

        name = self.name

        ready = self.ready

        crash = self.crash

        restart_count = self.restart_count

        has_previous_failure = self.has_previous_failure

        last_fail_condition: dict[str, Any] | None
        if isinstance(self.last_fail_condition, Schema774):
            last_fail_condition = self.last_fail_condition.to_dict()
        else:
            last_fail_condition = self.last_fail_condition

        phase = self.phase

        reason = self.reason

        created_at = self.created_at

        last_failure: dict[str, Any] | Unset = UNSET
        if not isinstance(self.last_failure, Unset):
            last_failure = self.last_failure.to_dict()

        waiting_reason = self.waiting_reason

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "ready": ready,
                "crash": crash,
                "restartCount": restart_count,
                "hasPreviousFailure": has_previous_failure,
                "lastFailCondition": last_fail_condition,
            }
        )
        if phase is not UNSET:
            field_dict["phase"] = phase
        if reason is not UNSET:
            field_dict["reason"] = reason
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if last_failure is not UNSET:
            field_dict["lastFailure"] = last_failure
        if waiting_reason is not UNSET:
            field_dict["waitingReason"] = waiting_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_774 import Schema774
        from ..models.schema_780 import Schema780

        d = dict(src_dict)
        name = d.pop("name")

        ready = d.pop("ready")

        crash = d.pop("crash")

        restart_count = d.pop("restartCount")

        has_previous_failure = d.pop("hasPreviousFailure")

        def _parse_last_fail_condition(data: object) -> None | Schema774:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema773_type_0 = Schema774.from_dict(data)

                return componentsschemas_schema773_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema774, data)

        last_fail_condition = _parse_last_fail_condition(d.pop("lastFailCondition"))

        phase = d.pop("phase", UNSET)

        reason = d.pop("reason", UNSET)

        created_at = d.pop("createdAt", UNSET)

        _last_failure = d.pop("lastFailure", UNSET)
        last_failure: Schema780 | Unset
        if isinstance(_last_failure, Unset):
            last_failure = UNSET
        else:
            last_failure = Schema780.from_dict(_last_failure)

        waiting_reason = d.pop("waitingReason", UNSET)

        deployment_status = cls(
            name=name,
            ready=ready,
            crash=crash,
            restart_count=restart_count,
            has_previous_failure=has_previous_failure,
            last_fail_condition=last_fail_condition,
            phase=phase,
            reason=reason,
            created_at=created_at,
            last_failure=last_failure,
            waiting_reason=waiting_reason,
        )

        return deployment_status
