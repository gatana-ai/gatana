from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema859")


@_attrs_define
class Schema859:
    """
    Attributes:
        type_ (Literal['mainContainerCrashBackOff'] | Literal['mainContainerImagePullBackOff']): Event type
            discriminator: "mainContainerCrashBackOff" or "mainContainerImagePullBackOff"
        reason (str): Reason for the back-off
        restarts (float): Number of restarts
        detail (str | Unset):
    """

    type_: Literal["mainContainerCrashBackOff"] | Literal["mainContainerImagePullBackOff"]
    reason: str
    restarts: float
    detail: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_: Literal["mainContainerCrashBackOff"] | Literal["mainContainerImagePullBackOff"]
        type_ = self.type_

        reason = self.reason

        restarts = self.restarts

        detail = self.detail

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "reason": reason,
                "restarts": restarts,
            }
        )
        if detail is not UNSET:
            field_dict["detail"] = detail

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_type_(
            data: object,
        ) -> Literal["mainContainerCrashBackOff"] | Literal["mainContainerImagePullBackOff"]:
            type_type_0 = cast(Literal["mainContainerCrashBackOff"], data)
            if type_type_0 != "mainContainerCrashBackOff":
                raise ValueError(f"type_type_0 must match const 'mainContainerCrashBackOff', got '{type_type_0}'")
            return type_type_0
            type_type_1 = cast(Literal["mainContainerImagePullBackOff"], data)
            if type_type_1 != "mainContainerImagePullBackOff":
                raise ValueError(f"type_type_1 must match const 'mainContainerImagePullBackOff', got '{type_type_1}'")
            return type_type_1

        type_ = _parse_type_(d.pop("type"))

        reason = d.pop("reason")

        restarts = d.pop("restarts")

        detail = d.pop("detail", UNSET)

        schema_859 = cls(
            type_=type_,
            reason=reason,
            restarts=restarts,
            detail=detail,
        )

        return schema_859
