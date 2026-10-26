from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="SetDefaultArtifactThemeResponse")


@_attrs_define
class SetDefaultArtifactThemeResponse:
    """
    Attributes:
        default_theme (str): 'gatana', 'none', or the id of an organization theme
    """

    default_theme: str

    def to_dict(self) -> dict[str, Any]:
        default_theme = self.default_theme

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "defaultTheme": default_theme,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        default_theme = d.pop("defaultTheme")

        set_default_artifact_theme_response = cls(
            default_theme=default_theme,
        )

        return set_default_artifact_theme_response
