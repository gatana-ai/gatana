from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="HashiCorpVaultConfigurationOutput")


@_attrs_define
class HashiCorpVaultConfigurationOutput:
    """
    Attributes:
        type_ (Literal['hashicorp_vault']):
        address (str):
        token (str):
        mount_path (str):
        namespace (str | Unset):
    """

    type_: Literal["hashicorp_vault"]
    address: str
    token: str
    mount_path: str
    namespace: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        address = self.address

        token = self.token

        mount_path = self.mount_path

        namespace = self.namespace

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "address": address,
                "token": token,
                "mountPath": mount_path,
            }
        )
        if namespace is not UNSET:
            field_dict["namespace"] = namespace

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["hashicorp_vault"], d.pop("type"))
        if type_ != "hashicorp_vault":
            raise ValueError(f"type must match const 'hashicorp_vault', got '{type_}'")

        address = d.pop("address")

        token = d.pop("token")

        mount_path = d.pop("mountPath")

        namespace = d.pop("namespace", UNSET)

        hashi_corp_vault_configuration_output = cls(
            type_=type_,
            address=address,
            token=token,
            mount_path=mount_path,
            namespace=namespace,
        )

        return hashi_corp_vault_configuration_output
