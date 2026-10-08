from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Literal, cast






T = TypeVar("T", bound="AwsSecretsManagerConfigurationOutput")



@_attrs_define
class AwsSecretsManagerConfigurationOutput:
    """ 
        Attributes:
            type_ (Literal['aws_secrets_manager']):
            region (str):
            access_key_id (str):
            secret_access_key (str):
     """

    type_: Literal['aws_secrets_manager']
    region: str
    access_key_id: str
    secret_access_key: str





    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        region = self.region

        access_key_id = self.access_key_id

        secret_access_key = self.secret_access_key


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "type": type_,
            "region": region,
            "accessKeyId": access_key_id,
            "secretAccessKey": secret_access_key,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal['aws_secrets_manager'] , d.pop("type"))
        if type_ != 'aws_secrets_manager':
            raise ValueError(f"type must match const 'aws_secrets_manager', got '{type_}'")

        region = d.pop("region")

        access_key_id = d.pop("accessKeyId")

        secret_access_key = d.pop("secretAccessKey")

        aws_secrets_manager_configuration_output = cls(
            type_=type_,
            region=region,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
        )

        return aws_secrets_manager_configuration_output

