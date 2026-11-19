from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.protection_mode import ProtectionMode

T = TypeVar("T", bound="NewServerProtectionModes")


@_attrs_define
class NewServerProtectionModes:
    """Protection modes for new servers. Use organization defaults, then built-in values

    Attributes:
        secrets (ProtectionMode):
        pii (ProtectionMode):
        injection (ProtectionMode):
    """

    secrets: ProtectionMode
    pii: ProtectionMode
    injection: ProtectionMode

    def to_dict(self) -> dict[str, Any]:
        secrets = self.secrets.value

        pii = self.pii.value

        injection = self.injection.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "secrets": secrets,
                "pii": pii,
                "injection": injection,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        secrets = ProtectionMode(d.pop("secrets"))

        pii = ProtectionMode(d.pop("pii"))

        injection = ProtectionMode(d.pop("injection"))

        new_server_protection_modes = cls(
            secrets=secrets,
            pii=pii,
            injection=injection,
        )

        return new_server_protection_modes
