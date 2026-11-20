from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_757 import Schema757
    from ..models.schema_764 import Schema764
    from ..models.schema_765 import Schema765


T = TypeVar("T", bound="ServerProtectionsOutput")


@_attrs_define
class ServerProtectionsOutput:
    """Built-in protections of the server. A missing protection is off

    Attributes:
        secrets (Schema757 | Unset):
        pii (Schema764 | Unset):
        injection (Schema765 | Unset):
    """

    secrets: Schema757 | Unset = UNSET
    pii: Schema764 | Unset = UNSET
    injection: Schema765 | Unset = UNSET

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
        from ..models.schema_757 import Schema757
        from ..models.schema_764 import Schema764
        from ..models.schema_765 import Schema765

        d = dict(src_dict)
        _secrets = d.pop("secrets", UNSET)
        secrets: Schema757 | Unset
        if isinstance(_secrets, Unset):
            secrets = UNSET
        else:
            secrets = Schema757.from_dict(_secrets)

        _pii = d.pop("pii", UNSET)
        pii: Schema764 | Unset
        if isinstance(_pii, Unset):
            pii = UNSET
        else:
            pii = Schema764.from_dict(_pii)

        _injection = d.pop("injection", UNSET)
        injection: Schema765 | Unset
        if isinstance(_injection, Unset):
            injection = UNSET
        else:
            injection = Schema765.from_dict(_injection)

        server_protections_output = cls(
            secrets=secrets,
            pii=pii,
            injection=injection,
        )

        return server_protections_output
