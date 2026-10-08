from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_463 import Schema463
from ..models.tool_refresh_credential_policy_output import ToolRefreshCredentialPolicyOutput
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema462")


@_attrs_define
class Schema462:
    """
    Attributes:
        method (Schema463): Authorization method that the server uses
        credentials_scope (Literal['server'] | Literal['user']): Whether credentials are shared for the whole server or
            stored per user
        tool_refresh_credential_policy (ToolRefreshCredentialPolicyOutput):
        apikeys (list[str] | Unset):
    """

    method: Schema463
    credentials_scope: Literal["server"] | Literal["user"]
    tool_refresh_credential_policy: ToolRefreshCredentialPolicyOutput
    apikeys: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        method = self.method.value

        credentials_scope: Literal["server"] | Literal["user"]
        credentials_scope = self.credentials_scope

        tool_refresh_credential_policy = self.tool_refresh_credential_policy.value

        apikeys: list[str] | Unset = UNSET
        if not isinstance(self.apikeys, Unset):
            apikeys = self.apikeys

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "method": method,
                "credentialsScope": credentials_scope,
                "toolRefreshCredentialPolicy": tool_refresh_credential_policy,
            }
        )
        if apikeys is not UNSET:
            field_dict["apikeys"] = apikeys

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        method = Schema463(d.pop("method"))

        def _parse_credentials_scope(data: object) -> Literal["server"] | Literal["user"]:
            componentsschemas_schema464_type_0 = cast(Literal["server"], data)
            if componentsschemas_schema464_type_0 != "server":
                raise ValueError(
                    f"/components/schemas/__schema464_type_0 must match const 'server', got '{componentsschemas_schema464_type_0}'"
                )
            return componentsschemas_schema464_type_0
            componentsschemas_schema464_type_1 = cast(Literal["user"], data)
            if componentsschemas_schema464_type_1 != "user":
                raise ValueError(
                    f"/components/schemas/__schema464_type_1 must match const 'user', got '{componentsschemas_schema464_type_1}'"
                )
            return componentsschemas_schema464_type_1

        credentials_scope = _parse_credentials_scope(d.pop("credentialsScope"))

        tool_refresh_credential_policy = ToolRefreshCredentialPolicyOutput(d.pop("toolRefreshCredentialPolicy"))

        apikeys = cast(list[str], d.pop("apikeys", UNSET))

        schema_462 = cls(
            method=method,
            credentials_scope=credentials_scope,
            tool_refresh_credential_policy=tool_refresh_credential_policy,
            apikeys=apikeys,
        )

        return schema_462
