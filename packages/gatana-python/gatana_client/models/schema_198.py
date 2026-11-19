from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_199 import Schema199
    from ..models.schema_206 import Schema206
    from ..models.schema_207 import Schema207


T = TypeVar("T", bound="Schema198")


@_attrs_define
class Schema198:
    """Built-in protections of the server. A missing protection is off

    Attributes:
        secrets (Schema199 | Unset):
        pii (Schema206 | Unset):
        injection (Schema207 | Unset):
    """

    secrets: Schema199 | Unset = UNSET
    pii: Schema206 | Unset = UNSET
    injection: Schema207 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

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
        field_dict.update(self.additional_properties)
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
        from ..models.schema_199 import Schema199
        from ..models.schema_206 import Schema206
        from ..models.schema_207 import Schema207

        d = dict(src_dict)
        _secrets = d.pop("secrets", UNSET)
        secrets: Schema199 | Unset
        if isinstance(_secrets, Unset):
            secrets = UNSET
        else:
            secrets = Schema199.from_dict(_secrets)

        _pii = d.pop("pii", UNSET)
        pii: Schema206 | Unset
        if isinstance(_pii, Unset):
            pii = UNSET
        else:
            pii = Schema206.from_dict(_pii)

        _injection = d.pop("injection", UNSET)
        injection: Schema207 | Unset
        if isinstance(_injection, Unset):
            injection = UNSET
        else:
            injection = Schema207.from_dict(_injection)

        schema_198 = cls(
            secrets=secrets,
            pii=pii,
            injection=injection,
        )

        schema_198.additional_properties = d
        return schema_198

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
