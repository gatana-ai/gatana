from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema774")


@_attrs_define
class Schema774:
    """
    Attributes:
        status (str): Status is the status of the condition. Can be True, False, Unknown. More info:
            https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle#pod-conditions
        type_ (str): Type of the condition (e.g. Ready, ContainersReady, PodScheduled)
        last_probe_time (str | Unset):
        last_transition_time (str | Unset):
        message (str | Unset):
        observed_generation (float | Unset):
        reason (str | Unset):
    """

    status: str
    type_: str
    last_probe_time: str | Unset = UNSET
    last_transition_time: str | Unset = UNSET
    message: str | Unset = UNSET
    observed_generation: float | Unset = UNSET
    reason: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        type_ = self.type_

        last_probe_time = self.last_probe_time

        last_transition_time = self.last_transition_time

        message = self.message

        observed_generation = self.observed_generation

        reason = self.reason

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "status": status,
                "type": type_,
            }
        )
        if last_probe_time is not UNSET:
            field_dict["lastProbeTime"] = last_probe_time
        if last_transition_time is not UNSET:
            field_dict["lastTransitionTime"] = last_transition_time
        if message is not UNSET:
            field_dict["message"] = message
        if observed_generation is not UNSET:
            field_dict["observedGeneration"] = observed_generation
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        type_ = d.pop("type")

        last_probe_time = d.pop("lastProbeTime", UNSET)

        last_transition_time = d.pop("lastTransitionTime", UNSET)

        message = d.pop("message", UNSET)

        observed_generation = d.pop("observedGeneration", UNSET)

        reason = d.pop("reason", UNSET)

        schema_774 = cls(
            status=status,
            type_=type_,
            last_probe_time=last_probe_time,
            last_transition_time=last_transition_time,
            message=message,
            observed_generation=observed_generation,
            reason=reason,
        )

        return schema_774
