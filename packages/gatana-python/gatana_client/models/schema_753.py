from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_754 import Schema754
    from ..models.schema_761 import Schema761
    from ..models.schema_762 import Schema762


T = TypeVar("T", bound="Schema753")


@_attrs_define
class Schema753:
    """Built-in protections of the server. A missing protection is off

    Attributes:
        secrets (Schema754 | Unset):
        pii (Schema761 | Unset):
        injection (Schema762 | Unset):
    """

    secrets: Schema754 | Unset = UNSET
    pii: Schema761 | Unset = UNSET
    injection: Schema762 | Unset = UNSET

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
        from ..models.schema_754 import Schema754
        from ..models.schema_761 import Schema761
        from ..models.schema_762 import Schema762

        d = dict(src_dict)
        _secrets = d.pop("secrets", UNSET)
        secrets: Schema754 | Unset
        if isinstance(_secrets, Unset):
            secrets = UNSET
        else:
            secrets = Schema754.from_dict(_secrets)

        _pii = d.pop("pii", UNSET)
        pii: Schema761 | Unset
        if isinstance(_pii, Unset):
            pii = UNSET
        else:
            pii = Schema761.from_dict(_pii)

        _injection = d.pop("injection", UNSET)
        injection: Schema762 | Unset
        if isinstance(_injection, Unset):
            injection = UNSET
        else:
            injection = Schema762.from_dict(_injection)

        schema_753 = cls(
            secrets=secrets,
            pii=pii,
            injection=injection,
        )

        return schema_753
