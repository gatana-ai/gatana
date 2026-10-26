from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SetDefaultArtifactThemeBody")


@_attrs_define
class SetDefaultArtifactThemeBody:
    """
    Attributes:
        theme (str): 'gatana' (Gatana styling), 'none' (the document as published), or an organization theme by id or by
            name
    """

    theme: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        theme = self.theme

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "theme": theme,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        theme = d.pop("theme")

        set_default_artifact_theme_body = cls(
            theme=theme,
        )

        set_default_artifact_theme_body.additional_properties = d
        return set_default_artifact_theme_body

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
