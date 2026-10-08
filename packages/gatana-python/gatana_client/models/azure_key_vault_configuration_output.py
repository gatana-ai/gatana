from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Literal, cast






T = TypeVar("T", bound="AzureKeyVaultConfigurationOutput")



@_attrs_define
class AzureKeyVaultConfigurationOutput:
    """ 
        Attributes:
            type_ (Literal['azure_key_vault']):
            vault_url (str):
            tenant_id (str):
            client_id (str):
            client_secret (str):
     """

    type_: Literal['azure_key_vault']
    vault_url: str
    tenant_id: str
    client_id: str
    client_secret: str





    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        vault_url = self.vault_url

        tenant_id = self.tenant_id

        client_id = self.client_id

        client_secret = self.client_secret


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "type": type_,
            "vaultUrl": vault_url,
            "tenantId": tenant_id,
            "clientId": client_id,
            "clientSecret": client_secret,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal['azure_key_vault'] , d.pop("type"))
        if type_ != 'azure_key_vault':
            raise ValueError(f"type must match const 'azure_key_vault', got '{type_}'")

        vault_url = d.pop("vaultUrl")

        tenant_id = d.pop("tenantId")

        client_id = d.pop("clientId")

        client_secret = d.pop("clientSecret")

        azure_key_vault_configuration_output = cls(
            type_=type_,
            vault_url=vault_url,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

        return azure_key_vault_configuration_output

