from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_561 import Schema561

if TYPE_CHECKING:
    from ..models.hosted_transport_config_output import HostedTransportConfigOutput
    from ..models.http_streaming_transport_config_output import HttpStreamingTransportConfigOutput
    from ..models.open_api_transport_config_output import OpenApiTransportConfigOutput
    from ..models.schema_462 import Schema462
    from ..models.schema_503 import Schema503
    from ..models.schema_575 import Schema575
    from ..models.server_o_auth_client_configuration import ServerOAuthClientConfiguration
    from ..models.server_o_auth_metadata import ServerOAuthMetadata
    from ..models.sse_transport_config_output import SseTransportConfigOutput
    from ..models.stdio_transport_config_output import StdioTransportConfigOutput


T = TypeVar("T", bound="ServerDto")


@_attrs_define
class ServerDto:
    """
    Attributes:
        id (str): Unique ID of the server
        slug (str): URL-friendly name of the server, unique within the tenant
        tenant_id (str): ID of the tenant that owns the server
        description (str): Human-readable description of the server
        authorization (Schema462):
        transport_config (HostedTransportConfigOutput | HttpStreamingTransportConfigOutput |
            OpenApiTransportConfigOutput | Schema503 | SseTransportConfigOutput | StdioTransportConfigOutput): Transport
            configuration used to connect to the server
        oauth_client_configuration (None | ServerOAuthClientConfiguration): OAuth client configuration, or null when not
            configured
        oauth_metadata (None | ServerOAuthMetadata): Discovered OAuth metadata, or null when not discovered
        visibility (Schema561):
        is_enabled (bool): Whether the server is enabled
        last_tool_refresh_at (None | str): Time of the last tool refresh, or null if tools were never refreshed
        mcp_protocol_version (str): MCP protocol version the server was last seen to speak, or empty if not yet detected
        mcp_protocol_detected_at (None | str): Time when the protocol version was last detected, or null if never
        timeout_protocol (int): Timeout in seconds for a single protocol request to the server
        timeout_total (int): Total timeout in seconds for a tool call, including progress notifications
        reset_timeout_on_progress_notification (bool): Whether a progress notification resets the protocol timeout
        is_output_compression_enabled (bool): Whether large tool outputs are compressed before they are returned to the
            client
        is_output_compression_transform_enabled (bool): Whether the compression transform step is applied to tool
            outputs
        output_compression_threshold_bytes (int): Minimum output size in bytes before compression is applied
        firewall_rules (list[Schema575]): Firewall rules evaluated against tool calls to the server
        created_at (str): Time when the server was created
        updated_at (str): Time when the server was last updated
    """

    id: str
    slug: str
    tenant_id: str
    description: str
    authorization: Schema462
    transport_config: (
        HostedTransportConfigOutput
        | HttpStreamingTransportConfigOutput
        | OpenApiTransportConfigOutput
        | Schema503
        | SseTransportConfigOutput
        | StdioTransportConfigOutput
    )
    oauth_client_configuration: None | ServerOAuthClientConfiguration
    oauth_metadata: None | ServerOAuthMetadata
    visibility: Schema561
    is_enabled: bool
    last_tool_refresh_at: None | str
    mcp_protocol_version: str
    mcp_protocol_detected_at: None | str
    timeout_protocol: int
    timeout_total: int
    reset_timeout_on_progress_notification: bool
    is_output_compression_enabled: bool
    is_output_compression_transform_enabled: bool
    output_compression_threshold_bytes: int
    firewall_rules: list[Schema575]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.hosted_transport_config_output import HostedTransportConfigOutput
        from ..models.http_streaming_transport_config_output import HttpStreamingTransportConfigOutput
        from ..models.schema_503 import Schema503
        from ..models.server_o_auth_client_configuration import ServerOAuthClientConfiguration
        from ..models.server_o_auth_metadata import ServerOAuthMetadata
        from ..models.sse_transport_config_output import SseTransportConfigOutput
        from ..models.stdio_transport_config_output import StdioTransportConfigOutput

        id = self.id

        slug = self.slug

        tenant_id = self.tenant_id

        description = self.description

        authorization = self.authorization.to_dict()

        transport_config: dict[str, Any]
        if isinstance(self.transport_config, HttpStreamingTransportConfigOutput):
            transport_config = self.transport_config.to_dict()
        elif isinstance(self.transport_config, StdioTransportConfigOutput):
            transport_config = self.transport_config.to_dict()
        elif isinstance(self.transport_config, SseTransportConfigOutput):
            transport_config = self.transport_config.to_dict()
        elif isinstance(self.transport_config, Schema503):
            transport_config = self.transport_config.to_dict()
        elif isinstance(self.transport_config, HostedTransportConfigOutput):
            transport_config = self.transport_config.to_dict()
        else:
            transport_config = self.transport_config.to_dict()

        oauth_client_configuration: dict[str, Any] | None
        if isinstance(self.oauth_client_configuration, ServerOAuthClientConfiguration):
            oauth_client_configuration = self.oauth_client_configuration.to_dict()
        else:
            oauth_client_configuration = self.oauth_client_configuration

        oauth_metadata: dict[str, Any] | None
        if isinstance(self.oauth_metadata, ServerOAuthMetadata):
            oauth_metadata = self.oauth_metadata.to_dict()
        else:
            oauth_metadata = self.oauth_metadata

        visibility = self.visibility.value

        is_enabled = self.is_enabled

        last_tool_refresh_at: None | str
        last_tool_refresh_at = self.last_tool_refresh_at

        mcp_protocol_version = self.mcp_protocol_version

        mcp_protocol_detected_at: None | str
        mcp_protocol_detected_at = self.mcp_protocol_detected_at

        timeout_protocol = self.timeout_protocol

        timeout_total = self.timeout_total

        reset_timeout_on_progress_notification = self.reset_timeout_on_progress_notification

        is_output_compression_enabled = self.is_output_compression_enabled

        is_output_compression_transform_enabled = self.is_output_compression_transform_enabled

        output_compression_threshold_bytes = self.output_compression_threshold_bytes

        firewall_rules = []
        for componentsschemas_schema574_item_data in self.firewall_rules:
            componentsschemas_schema574_item = componentsschemas_schema574_item_data.to_dict()
            firewall_rules.append(componentsschemas_schema574_item)

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "slug": slug,
                "tenantId": tenant_id,
                "description": description,
                "authorization": authorization,
                "transportConfig": transport_config,
                "oauthClientConfiguration": oauth_client_configuration,
                "oauthMetadata": oauth_metadata,
                "visibility": visibility,
                "isEnabled": is_enabled,
                "lastToolRefreshAt": last_tool_refresh_at,
                "mcpProtocolVersion": mcp_protocol_version,
                "mcpProtocolDetectedAt": mcp_protocol_detected_at,
                "timeoutProtocol": timeout_protocol,
                "timeoutTotal": timeout_total,
                "resetTimeoutOnProgressNotification": reset_timeout_on_progress_notification,
                "isOutputCompressionEnabled": is_output_compression_enabled,
                "isOutputCompressionTransformEnabled": is_output_compression_transform_enabled,
                "outputCompressionThresholdBytes": output_compression_threshold_bytes,
                "firewallRules": firewall_rules,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.hosted_transport_config_output import HostedTransportConfigOutput
        from ..models.http_streaming_transport_config_output import HttpStreamingTransportConfigOutput
        from ..models.open_api_transport_config_output import OpenApiTransportConfigOutput
        from ..models.schema_462 import Schema462
        from ..models.schema_503 import Schema503
        from ..models.schema_575 import Schema575
        from ..models.server_o_auth_client_configuration import ServerOAuthClientConfiguration
        from ..models.server_o_auth_metadata import ServerOAuthMetadata
        from ..models.sse_transport_config_output import SseTransportConfigOutput
        from ..models.stdio_transport_config_output import StdioTransportConfigOutput

        d = dict(src_dict)
        id = d.pop("id")

        slug = d.pop("slug")

        tenant_id = d.pop("tenantId")

        description = d.pop("description")

        authorization = Schema462.from_dict(d.pop("authorization"))

        def _parse_transport_config(
            data: object,
        ) -> (
            HostedTransportConfigOutput
            | HttpStreamingTransportConfigOutput
            | OpenApiTransportConfigOutput
            | Schema503
            | SseTransportConfigOutput
            | StdioTransportConfigOutput
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema470_type_0 = HttpStreamingTransportConfigOutput.from_dict(data)

                return componentsschemas_schema470_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema470_type_1 = StdioTransportConfigOutput.from_dict(data)

                return componentsschemas_schema470_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema470_type_2 = SseTransportConfigOutput.from_dict(data)

                return componentsschemas_schema470_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema470_type_3 = Schema503.from_dict(data)

                return componentsschemas_schema470_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema470_type_4 = HostedTransportConfigOutput.from_dict(data)

                return componentsschemas_schema470_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_schema470_type_5 = OpenApiTransportConfigOutput.from_dict(data)

            return componentsschemas_schema470_type_5

        transport_config = _parse_transport_config(d.pop("transportConfig"))

        def _parse_oauth_client_configuration(data: object) -> None | ServerOAuthClientConfiguration:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema525_type_1 = ServerOAuthClientConfiguration.from_dict(data)

                return componentsschemas_schema525_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServerOAuthClientConfiguration, data)

        oauth_client_configuration = _parse_oauth_client_configuration(d.pop("oauthClientConfiguration"))

        def _parse_oauth_metadata(data: object) -> None | ServerOAuthMetadata:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema539_type_1 = ServerOAuthMetadata.from_dict(data)

                return componentsschemas_schema539_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServerOAuthMetadata, data)

        oauth_metadata = _parse_oauth_metadata(d.pop("oauthMetadata"))

        visibility = Schema561(d.pop("visibility"))

        is_enabled = d.pop("isEnabled")

        def _parse_last_tool_refresh_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_tool_refresh_at = _parse_last_tool_refresh_at(d.pop("lastToolRefreshAt"))

        mcp_protocol_version = d.pop("mcpProtocolVersion")

        def _parse_mcp_protocol_detected_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        mcp_protocol_detected_at = _parse_mcp_protocol_detected_at(d.pop("mcpProtocolDetectedAt"))

        timeout_protocol = d.pop("timeoutProtocol")

        timeout_total = d.pop("timeoutTotal")

        reset_timeout_on_progress_notification = d.pop("resetTimeoutOnProgressNotification")

        is_output_compression_enabled = d.pop("isOutputCompressionEnabled")

        is_output_compression_transform_enabled = d.pop("isOutputCompressionTransformEnabled")

        output_compression_threshold_bytes = d.pop("outputCompressionThresholdBytes")

        firewall_rules = []
        _firewall_rules = d.pop("firewallRules")
        for componentsschemas_schema574_item_data in _firewall_rules:
            componentsschemas_schema574_item = Schema575.from_dict(componentsschemas_schema574_item_data)

            firewall_rules.append(componentsschemas_schema574_item)

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        server_dto = cls(
            id=id,
            slug=slug,
            tenant_id=tenant_id,
            description=description,
            authorization=authorization,
            transport_config=transport_config,
            oauth_client_configuration=oauth_client_configuration,
            oauth_metadata=oauth_metadata,
            visibility=visibility,
            is_enabled=is_enabled,
            last_tool_refresh_at=last_tool_refresh_at,
            mcp_protocol_version=mcp_protocol_version,
            mcp_protocol_detected_at=mcp_protocol_detected_at,
            timeout_protocol=timeout_protocol,
            timeout_total=timeout_total,
            reset_timeout_on_progress_notification=reset_timeout_on_progress_notification,
            is_output_compression_enabled=is_output_compression_enabled,
            is_output_compression_transform_enabled=is_output_compression_transform_enabled,
            output_compression_threshold_bytes=output_compression_threshold_bytes,
            firewall_rules=firewall_rules,
            created_at=created_at,
            updated_at=updated_at,
        )

        return server_dto
