from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Literal, cast






T = TypeVar("T", bound="GcpSecretManagerConfigurationOutput")



@_attrs_define
class GcpSecretManagerConfigurationOutput:
    """ 
        Attributes:
            type_ (Literal['gcp_secret_manager']):
            project_id (str):
            service_account_key (str):
     """

    type_: Literal['gcp_secret_manager']
    project_id: str
    service_account_key: str





    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        project_id = self.project_id

        service_account_key = self.service_account_key


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "type": type_,
            "projectId": project_id,
            "serviceAccountKey": service_account_key,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal['gcp_secret_manager'] , d.pop("type"))
        if type_ != 'gcp_secret_manager':
            raise ValueError(f"type must match const 'gcp_secret_manager', got '{type_}'")

        project_id = d.pop("projectId")

        service_account_key = d.pop("serviceAccountKey")

        gcp_secret_manager_configuration_output = cls(
            type_=type_,
            project_id=project_id,
            service_account_key=service_account_key,
        )

        return gcp_secret_manager_configuration_output

