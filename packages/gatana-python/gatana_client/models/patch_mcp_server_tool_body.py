from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.patch_mcp_server_tool_body_input_schema_override import PatchMcpServerToolBodyInputSchemaOverride


T = TypeVar("T", bound="PatchMcpServerToolBody")


@_attrs_define
class PatchMcpServerToolBody:
    """
    Attributes:
        description_override (str | Unset): Replacement description, applied when overrideDescription is true
        input_schema_override (PatchMcpServerToolBodyInputSchemaOverride | Unset): Replacement input schema, applied
            when overrideInputSchema is true
        override_description (bool | Unset): Whether descriptionOverride replaces the original description
        override_input_schema (bool | None | Unset): Whether inputSchemaOverride replaces the original input schema
        override_tool_name (bool | Unset): Whether toolNameOverride replaces the original tool name
        tool_name_override (str | Unset): Replacement tool name, applied when overrideToolName is true
        is_enabled (bool | Unset): Whether the tool is enabled and exposed to clients
    """

    description_override: str | Unset = UNSET
    input_schema_override: PatchMcpServerToolBodyInputSchemaOverride | Unset = UNSET
    override_description: bool | Unset = UNSET
    override_input_schema: bool | None | Unset = UNSET
    override_tool_name: bool | Unset = UNSET
    tool_name_override: str | Unset = UNSET
    is_enabled: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description_override = self.description_override

        input_schema_override: dict[str, Any] | Unset = UNSET
        if not isinstance(self.input_schema_override, Unset):
            input_schema_override = self.input_schema_override.to_dict()

        override_description = self.override_description

        override_input_schema: bool | None | Unset
        if isinstance(self.override_input_schema, Unset):
            override_input_schema = UNSET
        else:
            override_input_schema = self.override_input_schema

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
        if override_tool_name is not UNSET:
            field_dict["overrideToolName"] = override_tool_name
        if tool_name_override is not UNSET:
            field_dict["toolNameOverride"] = tool_name_override
        if is_enabled is not UNSET:
            field_dict["isEnabled"] = is_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_mcp_server_tool_body_input_schema_override import PatchMcpServerToolBodyInputSchemaOverride

        d = dict(src_dict)
        description_override = d.pop("descriptionOverride", UNSET)

        _input_schema_override = d.pop("inputSchemaOverride", UNSET)
        input_schema_override: PatchMcpServerToolBodyInputSchemaOverride | Unset
        if isinstance(_input_schema_override, Unset):
            input_schema_override = UNSET
        else:
            input_schema_override = PatchMcpServerToolBodyInputSchemaOverride.from_dict(_input_schema_override)

        override_description = d.pop("overrideDescription", UNSET)

        def _parse_override_input_schema(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        override_input_schema = _parse_override_input_schema(d.pop("overrideInputSchema", UNSET))

        override_tool_name = d.pop("overrideToolName", UNSET)

        tool_name_override = d.pop("toolNameOverride", UNSET)

        is_enabled = d.pop("isEnabled", UNSET)

        patch_mcp_server_tool_body = cls(
            description_override=description_override,
            input_schema_override=input_schema_override,
            override_description=override_description,
            override_input_schema=override_input_schema,
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
