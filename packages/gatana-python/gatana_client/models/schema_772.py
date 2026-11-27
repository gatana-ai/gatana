from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.resolved_protection import ResolvedProtection


T = TypeVar("T", bound="Schema772")


@_attrs_define
class Schema772:
    """
    Attributes:
        secrets (ResolvedProtection):
        pii (ResolvedProtection):
        injection (ResolvedProtection):
    """

    secrets: ResolvedProtection
    pii: ResolvedProtection
    injection: ResolvedProtection

    def to_dict(self) -> dict[str, Any]:
        secrets = self.secrets.to_dict()

        pii = self.pii.to_dict()

        injection = self.injection.to_dict()

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
        from ..models.resolved_protection import ResolvedProtection

        d = dict(src_dict)
        secrets = ResolvedProtection.from_dict(d.pop("secrets"))

        pii = ResolvedProtection.from_dict(d.pop("pii"))

        injection = ResolvedProtection.from_dict(d.pop("injection"))

        schema_772 = cls(
            secrets=secrets,
            pii=pii,
            injection=injection,
        )

        return schema_772
