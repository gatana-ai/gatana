from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Literal, cast






T = TypeVar("T", bound="InfisicalConfigurationOutput")



@_attrs_define
class InfisicalConfigurationOutput:
    """ 
        Attributes:
            type_ (Literal['infisical']):
            site_url (str):
            access_token (str):
            project_id (str):
            environment (str):
            secret_path (str):
     """

    type_: Literal['infisical']
    site_url: str
    access_token: str
    project_id: str
    environment: str
    secret_path: str





    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        site_url = self.site_url

        access_token = self.access_token

        project_id = self.project_id

        environment = self.environment

        secret_path = self.secret_path


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "type": type_,
            "siteUrl": site_url,
            "accessToken": access_token,
            "projectId": project_id,
            "environment": environment,
            "secretPath": secret_path,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal['infisical'] , d.pop("type"))
        if type_ != 'infisical':
            raise ValueError(f"type must match const 'infisical', got '{type_}'")

        site_url = d.pop("siteUrl")

        access_token = d.pop("accessToken")

        project_id = d.pop("projectId")

        environment = d.pop("environment")

        secret_path = d.pop("secretPath")

        infisical_configuration_output = cls(
            type_=type_,
            site_url=site_url,
            access_token=access_token,
            project_id=project_id,
            environment=environment,
            secret_path=secret_path,
        )

        return infisical_configuration_output

