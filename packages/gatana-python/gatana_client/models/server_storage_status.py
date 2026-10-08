from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="ServerStorageStatus")


@_attrs_define
class ServerStorageStatus:
    """
    Attributes:
        claim_name (str): Name of the underlying persistent volume claim
        phase (str): Claim phase reported by Kubernetes (e.g. Bound, Pending)
        requested_size (str): Size the claim asks for, in Kubernetes quantity format
        last_attached_at (None | str): Last time the volume was attached to a deployment, or null if never
        used_bytes (float | None): Bytes held on the volume, or null when its storage backend reports no usage
    """

    claim_name: str
    phase: str
    requested_size: str
    last_attached_at: None | str
    used_bytes: float | None

    def to_dict(self) -> dict[str, Any]:
        claim_name = self.claim_name

        phase = self.phase

        requested_size = self.requested_size

        last_attached_at: None | str
        last_attached_at = self.last_attached_at

        used_bytes: float | None
        used_bytes = self.used_bytes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "claimName": claim_name,
                "phase": phase,
                "requestedSize": requested_size,
                "lastAttachedAt": last_attached_at,
                "usedBytes": used_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        claim_name = d.pop("claimName")

        phase = d.pop("phase")

        requested_size = d.pop("requestedSize")

        def _parse_last_attached_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_attached_at = _parse_last_attached_at(d.pop("lastAttachedAt"))

        def _parse_used_bytes(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        used_bytes = _parse_used_bytes(d.pop("usedBytes"))

        server_storage_status = cls(
            claim_name=claim_name,
            phase=phase,
            requested_size=requested_size,
            last_attached_at=last_attached_at,
            used_bytes=used_bytes,
        )

        return server_storage_status
