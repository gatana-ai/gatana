from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_611 import Schema611
    from ..models.schema_613 import Schema613
    from ..models.schema_615 import Schema615
    from ..models.schema_619 import Schema619


T = TypeVar("T", bound="ServerToolDto")


@_attrs_define
class ServerToolDto:
    """
    Attributes:
        tenant_id (str): ID of the tenant that owns the tool
        tool_name (str): Tool name as reported by the MCP server
        description (str): Tool description as reported by the MCP server
        schema (Schema611): JSON schema for the tool input
        output_schema (None | Schema613): JSON schema for the tool output, or null if the server does not provide one
        annotations (None | Schema615): Tool annotations as reported by the MCP server, or null if none
        is_enabled (bool): Whether the tool is enabled and exposed to clients
        tool_name_override (str): Replacement tool name, applied when overrideToolName is true
        description_override (str): Replacement description, applied when overrideDescription is true
        input_schema_override (Schema619): Replacement input schema, applied when overrideInputSchema is true
        override_tool_name (bool): Whether toolNameOverride replaces the original tool name
        override_description (bool): Whether descriptionOverride replaces the original description
        override_input_schema (bool | None): Whether inputSchemaOverride replaces the original input schema
        server_slug (str):
        universal_name (str):
    """

    tenant_id: str
    tool_name: str
    description: str
    schema: Schema611
    output_schema: None | Schema613
    annotations: None | Schema615
    is_enabled: bool
    tool_name_override: str
    description_override: str
    input_schema_override: Schema619
    override_tool_name: bool
    override_description: bool
    override_input_schema: bool | None
    server_slug: str
    universal_name: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_613 import Schema613
        from ..models.schema_615 import Schema615

        tenant_id = self.tenant_id

        tool_name = self.tool_name

        description = self.description

        schema = self.schema.to_dict()

        output_schema: dict[str, Any] | None
        if isinstance(self.output_schema, Schema613):
            output_schema = self.output_schema.to_dict()
        else:
            output_schema = self.output_schema

        annotations: dict[str, Any] | None
        if isinstance(self.annotations, Schema615):
            annotations = self.annotations.to_dict()
        else:
            annotations = self.annotations

        is_enabled = self.is_enabled

        tool_name_override = self.tool_name_override

        description_override = self.description_override

        input_schema_override = self.input_schema_override.to_dict()

        override_tool_name = self.override_tool_name

        override_description = self.override_description

        override_input_schema: bool | None
        override_input_schema = self.override_input_schema

        server_slug = self.server_slug

        universal_name = self.universal_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tenantId": tenant_id,
                "toolName": tool_name,
                "description": description,
                "schema": schema,
                "outputSchema": output_schema,
                "annotations": annotations,
                "isEnabled": is_enabled,
                "toolNameOverride": tool_name_override,
                "descriptionOverride": description_override,
                "inputSchemaOverride": input_schema_override,
                "overrideToolName": override_tool_name,
                "overrideDescription": override_description,
                "overrideInputSchema": override_input_schema,
                "serverSlug": server_slug,
                "universalName": universal_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_611 import Schema611
        from ..models.schema_613 import Schema613
        from ..models.schema_615 import Schema615
        from ..models.schema_619 import Schema619

        d = dict(src_dict)
        tenant_id = d.pop("tenantId")

        tool_name = d.pop("toolName")

        description = d.pop("description")

        schema = Schema611.from_dict(d.pop("schema"))

        def _parse_output_schema(data: object) -> None | Schema613:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema612_type_0 = Schema613.from_dict(data)

                return componentsschemas_schema612_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema613, data)

        output_schema = _parse_output_schema(d.pop("outputSchema"))

        def _parse_annotations(data: object) -> None | Schema615:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema614_type_0 = Schema615.from_dict(data)

                return componentsschemas_schema614_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema615, data)

        annotations = _parse_annotations(d.pop("annotations"))

        is_enabled = d.pop("isEnabled")

        tool_name_override = d.pop("toolNameOverride")

        description_override = d.pop("descriptionOverride")

        input_schema_override = Schema619.from_dict(d.pop("inputSchemaOverride"))

        override_tool_name = d.pop("overrideToolName")

        override_description = d.pop("overrideDescription")

        def _parse_override_input_schema(data: object) -> bool | None:
            if data is None:
                return data
            return cast(bool | None, data)

        override_input_schema = _parse_override_input_schema(d.pop("overrideInputSchema"))

        server_slug = d.pop("serverSlug")

        universal_name = d.pop("universalName")

        server_tool_dto = cls(
            tenant_id=tenant_id,
            tool_name=tool_name,
            description=description,
            schema=schema,
            output_schema=output_schema,
            annotations=annotations,
            is_enabled=is_enabled,
            tool_name_override=tool_name_override,
            description_override=description_override,
            input_schema_override=input_schema_override,
            override_tool_name=override_tool_name,
            override_description=override_description,
            override_input_schema=override_input_schema,
            server_slug=server_slug,
            universal_name=universal_name,
        )

        return server_tool_dto
