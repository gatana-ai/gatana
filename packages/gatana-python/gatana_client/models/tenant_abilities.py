from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="TenantAbilities")


@_attrs_define
class TenantAbilities:
    """
    Attributes:
        can_have_multiple_users (bool):
        can_use_sandbox (bool):
        can_use_hosted_servers (bool):
        can_use_local_servers (bool):
        max_enabled_servers (float):
        can_use_ai_compression (bool):
        max_users (float):
        can_use_code_mode (bool):
        can_use_siem_streaming (bool):
        can_use_deployment_storage (bool):
        can_use_tailscale (bool):
        has_paid_features (bool):
    """

    can_have_multiple_users: bool
    can_use_sandbox: bool
    can_use_hosted_servers: bool
    can_use_local_servers: bool
    max_enabled_servers: float
    can_use_ai_compression: bool
    max_users: float
    can_use_code_mode: bool
    can_use_siem_streaming: bool
    can_use_deployment_storage: bool
    can_use_tailscale: bool
    has_paid_features: bool

    def to_dict(self) -> dict[str, Any]:
        can_have_multiple_users = self.can_have_multiple_users

        can_use_sandbox = self.can_use_sandbox

        can_use_hosted_servers = self.can_use_hosted_servers

        can_use_local_servers = self.can_use_local_servers

        max_enabled_servers = self.max_enabled_servers

        can_use_ai_compression = self.can_use_ai_compression

        max_users = self.max_users

        can_use_code_mode = self.can_use_code_mode

        can_use_siem_streaming = self.can_use_siem_streaming

        can_use_deployment_storage = self.can_use_deployment_storage

        can_use_tailscale = self.can_use_tailscale

        has_paid_features = self.has_paid_features

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "canHaveMultipleUsers": can_have_multiple_users,
                "canUseSandbox": can_use_sandbox,
                "canUseHostedServers": can_use_hosted_servers,
                "canUseLocalServers": can_use_local_servers,
                "maxEnabledServers": max_enabled_servers,
                "canUseAiCompression": can_use_ai_compression,
                "maxUsers": max_users,
                "canUseCodeMode": can_use_code_mode,
                "canUseSiemStreaming": can_use_siem_streaming,
                "canUseDeploymentStorage": can_use_deployment_storage,
                "canUseTailscale": can_use_tailscale,
                "hasPaidFeatures": has_paid_features,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        can_have_multiple_users = d.pop("canHaveMultipleUsers")

        can_use_sandbox = d.pop("canUseSandbox")

        can_use_hosted_servers = d.pop("canUseHostedServers")

        can_use_local_servers = d.pop("canUseLocalServers")

        max_enabled_servers = d.pop("maxEnabledServers")

        can_use_ai_compression = d.pop("canUseAiCompression")

        max_users = d.pop("maxUsers")

        can_use_code_mode = d.pop("canUseCodeMode")

        can_use_siem_streaming = d.pop("canUseSiemStreaming")

        can_use_deployment_storage = d.pop("canUseDeploymentStorage")

        can_use_tailscale = d.pop("canUseTailscale")

        has_paid_features = d.pop("hasPaidFeatures")

        tenant_abilities = cls(
            can_have_multiple_users=can_have_multiple_users,
            can_use_sandbox=can_use_sandbox,
            can_use_hosted_servers=can_use_hosted_servers,
            can_use_local_servers=can_use_local_servers,
            max_enabled_servers=max_enabled_servers,
            can_use_ai_compression=can_use_ai_compression,
            max_users=max_users,
            can_use_code_mode=can_use_code_mode,
            can_use_siem_streaming=can_use_siem_streaming,
            can_use_deployment_storage=can_use_deployment_storage,
            can_use_tailscale=can_use_tailscale,
            has_paid_features=has_paid_features,
        )

        return tenant_abilities
