from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="SiemHttpsTargetSettings")


@_attrs_define
class SiemHttpsTargetSettings:
    """
    Attributes:
        kind (Literal['https']): Send batches to an HTTPS endpoint
    """

    kind: Literal["https"]

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = cast(Literal["https"], d.pop("kind"))
        if kind != "https":
            raise ValueError(f"kind must match const 'https', got '{kind}'")

        siem_https_target_settings = cls(
            kind=kind,
        )

        return siem_https_target_settings
