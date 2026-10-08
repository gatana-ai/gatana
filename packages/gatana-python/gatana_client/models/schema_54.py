from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_55 import Schema55
from ..models.tool_refresh_credential_policy import ToolRefreshCredentialPolicy
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema54")


@_attrs_define
class Schema54:
    """
    Attributes:
        method (Schema55): Authorization method that the server uses
        credentials_scope (Literal['server'] | Literal['user']): Whether credentials are shared for the whole server or
            stored per user
        apikeys (list[str] | Unset):
        tool_refresh_credential_policy (ToolRefreshCredentialPolicy | Unset):
    """

    method: Schema55
    credentials_scope: Literal["server"] | Literal["user"]
    apikeys: list[str] | Unset = UNSET
    tool_refresh_credential_policy: ToolRefreshCredentialPolicy | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        method = self.method.value

        credentials_scope: Literal["server"] | Literal["user"]
        credentials_scope = self.credentials_scope

        apikeys: list[str] | Unset = UNSET
        if not isinstance(self.apikeys, Unset):
            apikeys = self.apikeys

        tool_refresh_credential_policy: str | Unset = UNSET
        if not isinstance(self.tool_refresh_credential_policy, Unset):
            tool_refresh_credential_policy = self.tool_refresh_credential_policy.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "method": method,
                "credentialsScope": credentials_scope,
            }
        )
        if apikeys is not UNSET:
            field_dict["apikeys"] = apikeys
        if tool_refresh_credential_policy is not UNSET:
            field_dict["toolRefreshCredentialPolicy"] = tool_refresh_credential_policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        method = Schema55(d.pop("method"))

        def _parse_credentials_scope(data: object) -> Literal["server"] | Literal["user"]:
            componentsschemas_schema56_type_0 = cast(Literal["server"], data)
            if componentsschemas_schema56_type_0 != "server":
                raise ValueError(
                    f"/components/schemas/__schema56_type_0 must match const 'server', got '{componentsschemas_schema56_type_0}'"
                )
            return componentsschemas_schema56_type_0
            componentsschemas_schema56_type_1 = cast(Literal["user"], data)
            if componentsschemas_schema56_type_1 != "user":
                raise ValueError(
                    f"/components/schemas/__schema56_type_1 must match const 'user', got '{componentsschemas_schema56_type_1}'"
                )
            return componentsschemas_schema56_type_1

        credentials_scope = _parse_credentials_scope(d.pop("credentialsScope"))

        apikeys = cast(list[str], d.pop("apikeys", UNSET))

        _tool_refresh_credential_policy = d.pop("toolRefreshCredentialPolicy", UNSET)
        tool_refresh_credential_policy: ToolRefreshCredentialPolicy | Unset
        if isinstance(_tool_refresh_credential_policy, Unset):
            tool_refresh_credential_policy = UNSET
        else:
            tool_refresh_credential_policy = ToolRefreshCredentialPolicy(_tool_refresh_credential_policy)

        schema_54 = cls(
            method=method,
            credentials_scope=credentials_scope,
            apikeys=apikeys,
            tool_refresh_credential_policy=tool_refresh_credential_policy,
        )

        schema_54.additional_properties = d
        return schema_54

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
