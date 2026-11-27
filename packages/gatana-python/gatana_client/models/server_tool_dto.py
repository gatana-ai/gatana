from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_829 import Schema829
    from ..models.schema_831 import Schema831
    from ..models.schema_833 import Schema833
    from ..models.schema_835 import Schema835
    from ..models.schema_840 import Schema840


T = TypeVar("T", bound="ServerToolDto")


@_attrs_define
class ServerToolDto:
    """
    Attributes:
        tenant_id (str): ID of the tenant that owns the tool
        tool_name (str): Tool name as reported by the MCP server
        description (str): Tool description as reported by the MCP server
        schema (Schema829): JSON schema for the tool input
        output_schema (None | Schema831): JSON schema for the tool output, or null if the server does not provide one
        annotations (None | Schema833): Tool annotations as reported by the MCP server, or null if none
        meta (None | Schema835): Tool metadata (_meta) from the MCP server, excluding Gatana keys. Null if absent
        is_enabled (bool): Whether the tool is enabled and exposed to clients
        tool_name_override (str): Replacement tool name, applied when overrideToolName is true
        description_override (str): Replacement description, applied when overrideDescription is true
        input_schema_override (None | Schema840): Use this schema when overrideInputSchema is true. Null means there is
            no replacement.
        override_tool_name (bool): Whether toolNameOverride replaces the original tool name
        override_description (bool): Whether descriptionOverride replaces the original description
        override_input_schema (bool | None): Whether inputSchemaOverride replaces the original input schema
        override_app_only (bool): Whether to list an app-only tool for models
        server_slug (str):
        universal_name (str):
    """

    tenant_id: str
    tool_name: str
    description: str
    schema: Schema829
    output_schema: None | Schema831
    annotations: None | Schema833
    meta: None | Schema835
    is_enabled: bool
    tool_name_override: str
    description_override: str
    input_schema_override: None | Schema840
    override_tool_name: bool
    override_description: bool
    override_input_schema: bool | None
    override_app_only: bool
    server_slug: str
    universal_name: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_831 import Schema831
        from ..models.schema_833 import Schema833
        from ..models.schema_835 import Schema835
        from ..models.schema_840 import Schema840

        tenant_id = self.tenant_id

        tool_name = self.tool_name

        description = self.description

        schema = self.schema.to_dict()

        output_schema: dict[str, Any] | None
        if isinstance(self.output_schema, Schema831):
            output_schema = self.output_schema.to_dict()
        else:
            output_schema = self.output_schema

        annotations: dict[str, Any] | None
        if isinstance(self.annotations, Schema833):
            annotations = self.annotations.to_dict()
        else:
            annotations = self.annotations

        meta: dict[str, Any] | None
        if isinstance(self.meta, Schema835):
            meta = self.meta.to_dict()
        else:
            meta = self.meta

        is_enabled = self.is_enabled

        tool_name_override = self.tool_name_override

        description_override = self.description_override

        input_schema_override: dict[str, Any] | None
        if isinstance(self.input_schema_override, Schema840):
            input_schema_override = self.input_schema_override.to_dict()
        else:
            input_schema_override = self.input_schema_override

        override_tool_name = self.override_tool_name

        override_description = self.override_description

        override_input_schema: bool | None
        override_input_schema = self.override_input_schema

        override_app_only = self.override_app_only

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
                "meta": meta,
                "isEnabled": is_enabled,
                "toolNameOverride": tool_name_override,
                "descriptionOverride": description_override,
                "inputSchemaOverride": input_schema_override,
                "overrideToolName": override_tool_name,
                "overrideDescription": override_description,
                "overrideInputSchema": override_input_schema,
                "overrideAppOnly": override_app_only,
                "serverSlug": server_slug,
                "universalName": universal_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_829 import Schema829
        from ..models.schema_831 import Schema831
        from ..models.schema_833 import Schema833
        from ..models.schema_835 import Schema835
        from ..models.schema_840 import Schema840

        d = dict(src_dict)
        tenant_id = d.pop("tenantId")

        tool_name = d.pop("toolName")

        description = d.pop("description")

        schema = Schema829.from_dict(d.pop("schema"))

        def _parse_output_schema(data: object) -> None | Schema831:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema830_type_0 = Schema831.from_dict(data)

                return componentsschemas_schema830_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema831, data)

        output_schema = _parse_output_schema(d.pop("outputSchema"))

        def _parse_annotations(data: object) -> None | Schema833:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema832_type_0 = Schema833.from_dict(data)

                return componentsschemas_schema832_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema833, data)

        annotations = _parse_annotations(d.pop("annotations"))

        def _parse_meta(data: object) -> None | Schema835:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema834_type_0 = Schema835.from_dict(data)

                return componentsschemas_schema834_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema835, data)

        meta = _parse_meta(d.pop("meta"))

        is_enabled = d.pop("isEnabled")

        tool_name_override = d.pop("toolNameOverride")

        description_override = d.pop("descriptionOverride")

        def _parse_input_schema_override(data: object) -> None | Schema840:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema839_type_0 = Schema840.from_dict(data)

                return componentsschemas_schema839_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema840, data)

        input_schema_override = _parse_input_schema_override(d.pop("inputSchemaOverride"))

        override_tool_name = d.pop("overrideToolName")

        override_description = d.pop("overrideDescription")

        def _parse_override_input_schema(data: object) -> bool | None:
            if data is None:
                return data
            return cast(bool | None, data)

        override_input_schema = _parse_override_input_schema(d.pop("overrideInputSchema"))

        override_app_only = d.pop("overrideAppOnly")

        server_slug = d.pop("serverSlug")

        universal_name = d.pop("universalName")

        server_tool_dto = cls(
            tenant_id=tenant_id,
            tool_name=tool_name,
            description=description,
            schema=schema,
            output_schema=output_schema,
            annotations=annotations,
            meta=meta,
            is_enabled=is_enabled,
            tool_name_override=tool_name_override,
            description_override=description_override,
            input_schema_override=input_schema_override,
            override_tool_name=override_tool_name,
            override_description=override_description,
            override_input_schema=override_input_schema,
            override_app_only=override_app_only,
            server_slug=server_slug,
            universal_name=universal_name,
        )

        return server_tool_dto
