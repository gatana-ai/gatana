from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_954 import Schema954
    from ..models.schema_959 import Schema959
    from ..models.schema_960 import Schema960


T = TypeVar("T", bound="ProtectionDefaults")


@_attrs_define
class ProtectionDefaults:
    """Organization protection defaults. Actions and settings apply to servers without their own values. An update replaces
    all defaults

        Attributes:
            secrets (Schema954 | Unset):
            pii (Schema959 | Unset):
            injection (Schema960 | Unset):
    """

    secrets: Schema954 | Unset = UNSET
    pii: Schema959 | Unset = UNSET
    injection: Schema960 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        secrets: dict[str, Any] | Unset = UNSET
        if not isinstance(self.secrets, Unset):
            secrets = self.secrets.to_dict()

        pii: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pii, Unset):
            pii = self.pii.to_dict()

        injection: dict[str, Any] | Unset = UNSET
        if not isinstance(self.injection, Unset):
            injection = self.injection.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if secrets is not UNSET:
            field_dict["secrets"] = secrets
        if pii is not UNSET:
            field_dict["pii"] = pii
        if injection is not UNSET:
            field_dict["injection"] = injection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_954 import Schema954
        from ..models.schema_959 import Schema959
        from ..models.schema_960 import Schema960

        d = dict(src_dict)
        _secrets = d.pop("secrets", UNSET)
        secrets: Schema954 | Unset
        if isinstance(_secrets, Unset):
            secrets = UNSET
        else:
            secrets = Schema954.from_dict(_secrets)

        _pii = d.pop("pii", UNSET)
        pii: Schema959 | Unset
        if isinstance(_pii, Unset):
            pii = UNSET
        else:
            pii = Schema959.from_dict(_pii)

        _injection = d.pop("injection", UNSET)
        injection: Schema960 | Unset
        if isinstance(_injection, Unset):
            injection = UNSET
        else:
            injection = Schema960.from_dict(_injection)

        protection_defaults = cls(
            secrets=secrets,
            pii=pii,
            injection=injection,
        )

        return protection_defaults
