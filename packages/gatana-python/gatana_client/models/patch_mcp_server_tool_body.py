from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_222 import Schema222


T = TypeVar("T", bound="PatchMcpServerToolBody")


@_attrs_define
class PatchMcpServerToolBody:
    """
    Attributes:
        description_override (str | Unset): Replacement description, applied when overrideDescription is true
        input_schema_override (None | Schema222 | Unset): Use this schema when overrideInputSchema is true. Null means
            there is no replacement.
        override_description (bool | Unset): Whether descriptionOverride replaces the original description
        override_input_schema (bool | None | Unset): Whether inputSchemaOverride replaces the original input schema
        override_app_only (bool | Unset): Whether to list an app-only tool for models
        override_tool_name (bool | Unset): Whether toolNameOverride replaces the original tool name
        tool_name_override (str | Unset): Replacement tool name, applied when overrideToolName is true
        is_enabled (bool | Unset): Whether the tool is enabled and exposed to clients
    """

    description_override: str | Unset = UNSET
    input_schema_override: None | Schema222 | Unset = UNSET
    override_description: bool | Unset = UNSET
    override_input_schema: bool | None | Unset = UNSET
    override_app_only: bool | Unset = UNSET
    override_tool_name: bool | Unset = UNSET
    tool_name_override: str | Unset = UNSET
    is_enabled: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_222 import Schema222

        description_override = self.description_override

        input_schema_override: dict[str, Any] | None | Unset
        if isinstance(self.input_schema_override, Unset):
            input_schema_override = UNSET
        elif isinstance(self.input_schema_override, Schema222):
            input_schema_override = self.input_schema_override.to_dict()
        else:
            input_schema_override = self.input_schema_override

        override_description = self.override_description

        override_input_schema: bool | None | Unset
        if isinstance(self.override_input_schema, Unset):
            override_input_schema = UNSET
        else:
            override_input_schema = self.override_input_schema

        override_app_only = self.override_app_only

        override_tool_name = self.override_tool_name

        tool_name_override = self.tool_name_override

        is_enabled = self.is_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description_override is not UNSET:
            field_dict["descriptionOverride"] = description_override
        if input_schema_override is not UNSET:
            field_dict["inputSchemaOverride"] = input_schema_override
        if override_description is not UNSET:
            field_dict["overrideDescription"] = override_description
        if override_input_schema is not UNSET:
            field_dict["overrideInputSchema"] = override_input_schema
        if override_app_only is not UNSET:
            field_dict["overrideAppOnly"] = override_app_only
        if override_tool_name is not UNSET:
            field_dict["overrideToolName"] = override_tool_name
        if tool_name_override is not UNSET:
            field_dict["toolNameOverride"] = tool_name_override
        if is_enabled is not UNSET:
            field_dict["isEnabled"] = is_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_222 import Schema222

        d = dict(src_dict)
        description_override = d.pop("descriptionOverride", UNSET)

        def _parse_input_schema_override(data: object) -> None | Schema222 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_schema_override_type_0 = Schema222.from_dict(data)

                return input_schema_override_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema222 | Unset, data)

        input_schema_override = _parse_input_schema_override(d.pop("inputSchemaOverride", UNSET))

        override_description = d.pop("overrideDescription", UNSET)

        def _parse_override_input_schema(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        override_input_schema = _parse_override_input_schema(d.pop("overrideInputSchema", UNSET))

        override_app_only = d.pop("overrideAppOnly", UNSET)

        override_tool_name = d.pop("overrideToolName", UNSET)

        tool_name_override = d.pop("toolNameOverride", UNSET)

        is_enabled = d.pop("isEnabled", UNSET)

        patch_mcp_server_tool_body = cls(
            description_override=description_override,
            input_schema_override=input_schema_override,
            override_description=override_description,
            override_input_schema=override_input_schema,
            override_app_only=override_app_only,
            override_tool_name=override_tool_name,
            tool_name_override=tool_name_override,
            is_enabled=is_enabled,
        )

        patch_mcp_server_tool_body.additional_properties = d
        return patch_mcp_server_tool_body

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
