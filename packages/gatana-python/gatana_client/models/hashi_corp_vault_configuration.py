from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HashiCorpVaultConfiguration")


@_attrs_define
class HashiCorpVaultConfiguration:
    """
    Attributes:
        type_ (Literal['hashicorp_vault']):
        address (str):
        token (str):
        namespace (str | Unset):
        mount_path (str | Unset):
    """

    type_: Literal["hashicorp_vault"]
    address: str
    token: str
    namespace: str | Unset = UNSET
    mount_path: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        address = self.address

        token = self.token

        namespace = self.namespace

        mount_path = self.mount_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "address": address,
                "token": token,
            }
        )
        if namespace is not UNSET:
            field_dict["namespace"] = namespace
        if mount_path is not UNSET:
            field_dict["mountPath"] = mount_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["hashicorp_vault"], d.pop("type"))
        if type_ != "hashicorp_vault":
            raise ValueError(f"type must match const 'hashicorp_vault', got '{type_}'")

        address = d.pop("address")

        token = d.pop("token")

        namespace = d.pop("namespace", UNSET)

        mount_path = d.pop("mountPath", UNSET)

        hashi_corp_vault_configuration = cls(
            type_=type_,
            address=address,
            token=token,
            namespace=namespace,
            mount_path=mount_path,
        )

        hashi_corp_vault_configuration.additional_properties = d
        return hashi_corp_vault_configuration

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
