from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_353 import Schema353
from ..models.schema_709 import Schema709
from ..models.schema_713 import Schema713
from ..models.schema_733 import Schema733
from ..models.schema_734 import Schema734

if TYPE_CHECKING:
    from ..models.assistant_llm_configuration_status import AssistantLlmConfigurationStatus
    from ..models.schema_715 import Schema715
    from ..models.schema_716 import Schema716
    from ..models.schema_717 import Schema717
    from ..models.tenant_oidc_configuration import TenantOidcConfiguration
    from ..models.tenant_saml_configuration import TenantSamlConfiguration


T = TypeVar("T", bound="TenantDto")


@_attrs_define
class TenantDto:
    """
    Attributes:
        id (str): Unique ID of the tenant
        is_playground (bool): Whether the tenant is a playground tenant
        display_name (str): Display name of the tenant
        upstream_oidc_configuration (None | TenantOidcConfiguration): External OIDC identity provider configuration, or
            null when not configured
        upstream_saml_configuration (None | TenantSamlConfiguration): External SAML identity provider configuration, or
            null when not configured
        is_upstream_oidc_tokens_trusted (bool): Whether access tokens issued by the upstream OIDC provider are accepted
            for MCP authorization
        is_automatic_seat_increase_enabled (bool): Whether the subscription seat count increases automatically when new
            members join
        is_mcp_authorization_api_key_enabled (bool): Whether API keys can be used to authorize MCP access
        grant_permissions_new_tool_policy (bool): Whether newly discovered tools are enabled automatically
        allow_member_add_remote_servers (bool): Whether members can add remote servers (httpstreaming, sse, openapi)
        allow_member_add_local_servers (bool): Whether members can add local (stdio) servers
        allow_member_add_hosted_servers (bool): Whether members can add hosted servers
        is_google_refresh_token_saving_enabled (bool): Whether Google OAuth refresh tokens are saved for the tenant
        is_output_compression_allowed (bool): Whether tool output compression is allowed for servers of the tenant
        is_output_compression_ai_enabled (bool): Whether AI-based output compression is enabled
        is_code_mode_auto_trigger_enabled (bool): Whether code mode is enabled automatically when the tool count exceeds
            the threshold
        code_mode_auto_trigger_threshold (int | None): Number of tools above which code mode is enabled automatically,
            or null for the default
        output_compression_ai_model (Schema709): Model variant used for AI-based output compression
        member_default_role (Literal['none'] | Schema353): Default server role for members, or "none" for no default
            access
        is_owner_all_tools_over_mcp_enabled (bool): Whether an owner is offered every tool of the organization over MCP.
            When false, an owner gets the tools of the servers they hold a grant on, the way a member does
        mcp_audit_log_level (Schema713):
        mcp_audit_logging_include_protocol_messages (bool): Whether MCP audit log entries include the protocol messages
        default_resource_limits (Schema715):
        default_resource_requests (Schema716):
        deployment_resource_limits (Schema717):
        deployment_storage_quota (str): Total size of persistent volumes the organization may claim across its
            deployments, in Kubernetes quantity format (e.g. "20Gi"). This caps what may be claimed/allocated and not what
            is written/used.
        is_assistant_enabled (bool): Whether the in-app AI assistant is available to members
        is_assistant_byok_enabled (bool): Whether the assistant uses the organization's own model endpoint instead of
            the platform's
        assistant_platform_processing_accepted_at (None | str): Time an owner instructed Gatana to process assistant
            conversations through Gatana's model provider, or null if never given
        assistant_platform_processing_accepted_by (None | str): ID of the user who gave that instruction, or null if it
            was never given
        is_assistant_conversation_sharing_enabled (bool): Whether a paying organization has agreed that Gatana may keep
            a reduced copy of its assistant conversations to improve the assistant. Not written for an organization on the
            free plan, where sharing follows from the plan
        assistant_conversation_sharing_accepted_at (None | str): Time an owner agreed to that, or null if never given
        assistant_conversation_sharing_accepted_by (None | str): ID of the user who agreed to it, or null if it was
            never given
        assistant_daily_token_limit (int | None): Maximum number of AI assistant tokens the tenant may spend per day, or
            null for the default
        is_scim_enabled (bool): Whether SCIM provisioning is enabled
        scim_group_delete_behavior (Schema733): What happens to a team when its SCIM group is deleted
        scim_user_delete_behavior (Schema734): What happens to a user when it is deleted through SCIM
        assistant_llm_configuration_status (AssistantLlmConfigurationStatus | None): The organization's own model
            endpoint for the assistant without its credentials, or null when none is stored
    """

    id: str
    is_playground: bool
    display_name: str
    upstream_oidc_configuration: None | TenantOidcConfiguration
    upstream_saml_configuration: None | TenantSamlConfiguration
    is_upstream_oidc_tokens_trusted: bool
    is_automatic_seat_increase_enabled: bool
    is_mcp_authorization_api_key_enabled: bool
    grant_permissions_new_tool_policy: bool
    allow_member_add_remote_servers: bool
    allow_member_add_local_servers: bool
    allow_member_add_hosted_servers: bool
    is_google_refresh_token_saving_enabled: bool
    is_output_compression_allowed: bool
    is_output_compression_ai_enabled: bool
    is_code_mode_auto_trigger_enabled: bool
    code_mode_auto_trigger_threshold: int | None
    output_compression_ai_model: Schema709
    member_default_role: Literal["none"] | Schema353
    is_owner_all_tools_over_mcp_enabled: bool
    mcp_audit_log_level: Schema713
    mcp_audit_logging_include_protocol_messages: bool
    default_resource_limits: Schema715
    default_resource_requests: Schema716
    deployment_resource_limits: Schema717
    deployment_storage_quota: str
    is_assistant_enabled: bool
    is_assistant_byok_enabled: bool
    assistant_platform_processing_accepted_at: None | str
    assistant_platform_processing_accepted_by: None | str
    is_assistant_conversation_sharing_enabled: bool
    assistant_conversation_sharing_accepted_at: None | str
    assistant_conversation_sharing_accepted_by: None | str
    assistant_daily_token_limit: int | None
    is_scim_enabled: bool
    scim_group_delete_behavior: Schema733
    scim_user_delete_behavior: Schema734
    assistant_llm_configuration_status: AssistantLlmConfigurationStatus | None

    def to_dict(self) -> dict[str, Any]:
        from ..models.assistant_llm_configuration_status import AssistantLlmConfigurationStatus
        from ..models.tenant_oidc_configuration import TenantOidcConfiguration
        from ..models.tenant_saml_configuration import TenantSamlConfiguration

        id = self.id

        is_playground = self.is_playground

        display_name = self.display_name

        upstream_oidc_configuration: dict[str, Any] | None
        if isinstance(self.upstream_oidc_configuration, TenantOidcConfiguration):
            upstream_oidc_configuration = self.upstream_oidc_configuration.to_dict()
        else:
            upstream_oidc_configuration = self.upstream_oidc_configuration

        upstream_saml_configuration: dict[str, Any] | None
        if isinstance(self.upstream_saml_configuration, TenantSamlConfiguration):
            upstream_saml_configuration = self.upstream_saml_configuration.to_dict()
        else:
            upstream_saml_configuration = self.upstream_saml_configuration

        is_upstream_oidc_tokens_trusted = self.is_upstream_oidc_tokens_trusted

        is_automatic_seat_increase_enabled = self.is_automatic_seat_increase_enabled

        is_mcp_authorization_api_key_enabled = self.is_mcp_authorization_api_key_enabled

        grant_permissions_new_tool_policy = self.grant_permissions_new_tool_policy

        allow_member_add_remote_servers = self.allow_member_add_remote_servers

        allow_member_add_local_servers = self.allow_member_add_local_servers

        allow_member_add_hosted_servers = self.allow_member_add_hosted_servers

        is_google_refresh_token_saving_enabled = self.is_google_refresh_token_saving_enabled

        is_output_compression_allowed = self.is_output_compression_allowed

        is_output_compression_ai_enabled = self.is_output_compression_ai_enabled

        is_code_mode_auto_trigger_enabled = self.is_code_mode_auto_trigger_enabled

        code_mode_auto_trigger_threshold: int | None
        code_mode_auto_trigger_threshold = self.code_mode_auto_trigger_threshold

        output_compression_ai_model = self.output_compression_ai_model.value

        member_default_role: Literal["none"] | str
        if isinstance(self.member_default_role, Schema353):
            member_default_role = self.member_default_role.value
        else:
            member_default_role = self.member_default_role

        is_owner_all_tools_over_mcp_enabled = self.is_owner_all_tools_over_mcp_enabled

        mcp_audit_log_level = self.mcp_audit_log_level.value

        mcp_audit_logging_include_protocol_messages = self.mcp_audit_logging_include_protocol_messages

        default_resource_limits = self.default_resource_limits.to_dict()

        default_resource_requests = self.default_resource_requests.to_dict()

        deployment_resource_limits = self.deployment_resource_limits.to_dict()

        deployment_storage_quota = self.deployment_storage_quota

        is_assistant_enabled = self.is_assistant_enabled

        is_assistant_byok_enabled = self.is_assistant_byok_enabled

        assistant_platform_processing_accepted_at: None | str
        assistant_platform_processing_accepted_at = self.assistant_platform_processing_accepted_at

        assistant_platform_processing_accepted_by: None | str
        assistant_platform_processing_accepted_by = self.assistant_platform_processing_accepted_by

        is_assistant_conversation_sharing_enabled = self.is_assistant_conversation_sharing_enabled

        assistant_conversation_sharing_accepted_at: None | str
        assistant_conversation_sharing_accepted_at = self.assistant_conversation_sharing_accepted_at

        assistant_conversation_sharing_accepted_by: None | str
        assistant_conversation_sharing_accepted_by = self.assistant_conversation_sharing_accepted_by

        assistant_daily_token_limit: int | None
        assistant_daily_token_limit = self.assistant_daily_token_limit

        is_scim_enabled = self.is_scim_enabled

        scim_group_delete_behavior = self.scim_group_delete_behavior.value

        scim_user_delete_behavior = self.scim_user_delete_behavior.value

        assistant_llm_configuration_status: dict[str, Any] | None
        if isinstance(self.assistant_llm_configuration_status, AssistantLlmConfigurationStatus):
            assistant_llm_configuration_status = self.assistant_llm_configuration_status.to_dict()
        else:
            assistant_llm_configuration_status = self.assistant_llm_configuration_status

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "isPlayground": is_playground,
                "displayName": display_name,
                "upstreamOidcConfiguration": upstream_oidc_configuration,
                "upstreamSamlConfiguration": upstream_saml_configuration,
                "isUpstreamOidcTokensTrusted": is_upstream_oidc_tokens_trusted,
                "isAutomaticSeatIncreaseEnabled": is_automatic_seat_increase_enabled,
                "isMcpAuthorizationApiKeyEnabled": is_mcp_authorization_api_key_enabled,
                "grantPermissionsNewToolPolicy": grant_permissions_new_tool_policy,
                "allowMemberAddRemoteServers": allow_member_add_remote_servers,
                "allowMemberAddLocalServers": allow_member_add_local_servers,
                "allowMemberAddHostedServers": allow_member_add_hosted_servers,
                "isGoogleRefreshTokenSavingEnabled": is_google_refresh_token_saving_enabled,
                "isOutputCompressionAllowed": is_output_compression_allowed,
                "isOutputCompressionAiEnabled": is_output_compression_ai_enabled,
                "isCodeModeAutoTriggerEnabled": is_code_mode_auto_trigger_enabled,
                "codeModeAutoTriggerThreshold": code_mode_auto_trigger_threshold,
                "outputCompressionAiModel": output_compression_ai_model,
                "memberDefaultRole": member_default_role,
                "isOwnerAllToolsOverMcpEnabled": is_owner_all_tools_over_mcp_enabled,
                "mcpAuditLogLevel": mcp_audit_log_level,
                "mcpAuditLoggingIncludeProtocolMessages": mcp_audit_logging_include_protocol_messages,
                "defaultResourceLimits": default_resource_limits,
                "defaultResourceRequests": default_resource_requests,
                "deploymentResourceLimits": deployment_resource_limits,
                "deploymentStorageQuota": deployment_storage_quota,
                "isAssistantEnabled": is_assistant_enabled,
                "isAssistantByokEnabled": is_assistant_byok_enabled,
                "assistantPlatformProcessingAcceptedAt": assistant_platform_processing_accepted_at,
                "assistantPlatformProcessingAcceptedBy": assistant_platform_processing_accepted_by,
                "isAssistantConversationSharingEnabled": is_assistant_conversation_sharing_enabled,
                "assistantConversationSharingAcceptedAt": assistant_conversation_sharing_accepted_at,
                "assistantConversationSharingAcceptedBy": assistant_conversation_sharing_accepted_by,
                "assistantDailyTokenLimit": assistant_daily_token_limit,
                "isScimEnabled": is_scim_enabled,
                "scimGroupDeleteBehavior": scim_group_delete_behavior,
                "scimUserDeleteBehavior": scim_user_delete_behavior,
                "assistantLlmConfigurationStatus": assistant_llm_configuration_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.assistant_llm_configuration_status import AssistantLlmConfigurationStatus
        from ..models.schema_715 import Schema715
        from ..models.schema_716 import Schema716
        from ..models.schema_717 import Schema717
        from ..models.tenant_oidc_configuration import TenantOidcConfiguration
        from ..models.tenant_saml_configuration import TenantSamlConfiguration

        d = dict(src_dict)
        id = d.pop("id")

        is_playground = d.pop("isPlayground")

        display_name = d.pop("displayName")

        def _parse_upstream_oidc_configuration(data: object) -> None | TenantOidcConfiguration:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema670_type_0 = TenantOidcConfiguration.from_dict(data)

                return componentsschemas_schema670_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TenantOidcConfiguration, data)

        upstream_oidc_configuration = _parse_upstream_oidc_configuration(d.pop("upstreamOidcConfiguration"))

        def _parse_upstream_saml_configuration(data: object) -> None | TenantSamlConfiguration:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema684_type_0 = TenantSamlConfiguration.from_dict(data)

                return componentsschemas_schema684_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TenantSamlConfiguration, data)

        upstream_saml_configuration = _parse_upstream_saml_configuration(d.pop("upstreamSamlConfiguration"))

        is_upstream_oidc_tokens_trusted = d.pop("isUpstreamOidcTokensTrusted")

        is_automatic_seat_increase_enabled = d.pop("isAutomaticSeatIncreaseEnabled")

        is_mcp_authorization_api_key_enabled = d.pop("isMcpAuthorizationApiKeyEnabled")

        grant_permissions_new_tool_policy = d.pop("grantPermissionsNewToolPolicy")

        allow_member_add_remote_servers = d.pop("allowMemberAddRemoteServers")

        allow_member_add_local_servers = d.pop("allowMemberAddLocalServers")

        allow_member_add_hosted_servers = d.pop("allowMemberAddHostedServers")

        is_google_refresh_token_saving_enabled = d.pop("isGoogleRefreshTokenSavingEnabled")

        is_output_compression_allowed = d.pop("isOutputCompressionAllowed")

        is_output_compression_ai_enabled = d.pop("isOutputCompressionAiEnabled")

        is_code_mode_auto_trigger_enabled = d.pop("isCodeModeAutoTriggerEnabled")

        def _parse_code_mode_auto_trigger_threshold(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        code_mode_auto_trigger_threshold = _parse_code_mode_auto_trigger_threshold(
            d.pop("codeModeAutoTriggerThreshold")
        )

        output_compression_ai_model = Schema709(d.pop("outputCompressionAiModel"))

        def _parse_member_default_role(data: object) -> Literal["none"] | Schema353:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_schema710_type_0 = Schema353(data)

                return componentsschemas_schema710_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            componentsschemas_schema710_type_1 = cast(Literal["none"], data)
            if componentsschemas_schema710_type_1 != "none":
                raise ValueError(
                    f"/components/schemas/__schema710_type_1 must match const 'none', got '{componentsschemas_schema710_type_1}'"
                )
            return componentsschemas_schema710_type_1

        member_default_role = _parse_member_default_role(d.pop("memberDefaultRole"))

        is_owner_all_tools_over_mcp_enabled = d.pop("isOwnerAllToolsOverMcpEnabled")

        mcp_audit_log_level = Schema713(d.pop("mcpAuditLogLevel"))

        mcp_audit_logging_include_protocol_messages = d.pop("mcpAuditLoggingIncludeProtocolMessages")

        default_resource_limits = Schema715.from_dict(d.pop("defaultResourceLimits"))

        default_resource_requests = Schema716.from_dict(d.pop("defaultResourceRequests"))

        deployment_resource_limits = Schema717.from_dict(d.pop("deploymentResourceLimits"))

        deployment_storage_quota = d.pop("deploymentStorageQuota")

        is_assistant_enabled = d.pop("isAssistantEnabled")

        is_assistant_byok_enabled = d.pop("isAssistantByokEnabled")

        def _parse_assistant_platform_processing_accepted_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        assistant_platform_processing_accepted_at = _parse_assistant_platform_processing_accepted_at(
            d.pop("assistantPlatformProcessingAcceptedAt")
        )

        def _parse_assistant_platform_processing_accepted_by(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        assistant_platform_processing_accepted_by = _parse_assistant_platform_processing_accepted_by(
            d.pop("assistantPlatformProcessingAcceptedBy")
        )

        is_assistant_conversation_sharing_enabled = d.pop("isAssistantConversationSharingEnabled")

        def _parse_assistant_conversation_sharing_accepted_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        assistant_conversation_sharing_accepted_at = _parse_assistant_conversation_sharing_accepted_at(
            d.pop("assistantConversationSharingAcceptedAt")
        )

        def _parse_assistant_conversation_sharing_accepted_by(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        assistant_conversation_sharing_accepted_by = _parse_assistant_conversation_sharing_accepted_by(
            d.pop("assistantConversationSharingAcceptedBy")
        )

        def _parse_assistant_daily_token_limit(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        assistant_daily_token_limit = _parse_assistant_daily_token_limit(d.pop("assistantDailyTokenLimit"))

        is_scim_enabled = d.pop("isScimEnabled")

        scim_group_delete_behavior = Schema733(d.pop("scimGroupDeleteBehavior"))

        scim_user_delete_behavior = Schema734(d.pop("scimUserDeleteBehavior"))

        def _parse_assistant_llm_configuration_status(data: object) -> AssistantLlmConfigurationStatus | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema735_type_0 = AssistantLlmConfigurationStatus.from_dict(data)

                return componentsschemas_schema735_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AssistantLlmConfigurationStatus | None, data)

        assistant_llm_configuration_status = _parse_assistant_llm_configuration_status(
            d.pop("assistantLlmConfigurationStatus")
        )

        tenant_dto = cls(
            id=id,
            is_playground=is_playground,
            display_name=display_name,
            upstream_oidc_configuration=upstream_oidc_configuration,
            upstream_saml_configuration=upstream_saml_configuration,
            is_upstream_oidc_tokens_trusted=is_upstream_oidc_tokens_trusted,
            is_automatic_seat_increase_enabled=is_automatic_seat_increase_enabled,
            is_mcp_authorization_api_key_enabled=is_mcp_authorization_api_key_enabled,
            grant_permissions_new_tool_policy=grant_permissions_new_tool_policy,
            allow_member_add_remote_servers=allow_member_add_remote_servers,
            allow_member_add_local_servers=allow_member_add_local_servers,
            allow_member_add_hosted_servers=allow_member_add_hosted_servers,
            is_google_refresh_token_saving_enabled=is_google_refresh_token_saving_enabled,
            is_output_compression_allowed=is_output_compression_allowed,
            is_output_compression_ai_enabled=is_output_compression_ai_enabled,
            is_code_mode_auto_trigger_enabled=is_code_mode_auto_trigger_enabled,
            code_mode_auto_trigger_threshold=code_mode_auto_trigger_threshold,
            output_compression_ai_model=output_compression_ai_model,
            member_default_role=member_default_role,
            is_owner_all_tools_over_mcp_enabled=is_owner_all_tools_over_mcp_enabled,
            mcp_audit_log_level=mcp_audit_log_level,
            mcp_audit_logging_include_protocol_messages=mcp_audit_logging_include_protocol_messages,
            default_resource_limits=default_resource_limits,
            default_resource_requests=default_resource_requests,
            deployment_resource_limits=deployment_resource_limits,
            deployment_storage_quota=deployment_storage_quota,
            is_assistant_enabled=is_assistant_enabled,
            is_assistant_byok_enabled=is_assistant_byok_enabled,
            assistant_platform_processing_accepted_at=assistant_platform_processing_accepted_at,
            assistant_platform_processing_accepted_by=assistant_platform_processing_accepted_by,
            is_assistant_conversation_sharing_enabled=is_assistant_conversation_sharing_enabled,
            assistant_conversation_sharing_accepted_at=assistant_conversation_sharing_accepted_at,
            assistant_conversation_sharing_accepted_by=assistant_conversation_sharing_accepted_by,
            assistant_daily_token_limit=assistant_daily_token_limit,
            is_scim_enabled=is_scim_enabled,
            scim_group_delete_behavior=scim_group_delete_behavior,
            scim_user_delete_behavior=scim_user_delete_behavior,
            assistant_llm_configuration_status=assistant_llm_configuration_status,
        )

        return tenant_dto
