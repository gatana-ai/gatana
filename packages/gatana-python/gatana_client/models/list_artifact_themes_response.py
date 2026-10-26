from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.artifact_theme_summary_dto import ArtifactThemeSummaryDto


T = TypeVar("T", bound="ListArtifactThemesResponse")


@_attrs_define
class ListArtifactThemesResponse:
    """
    Attributes:
        themes (list[ArtifactThemeSummaryDto]): The organization themes, by name
        default_theme (str): The theme new artifacts get when their creator names none: 'gatana', 'none', or the id of
            an organization theme
    """

    themes: list[ArtifactThemeSummaryDto]
    default_theme: str

    def to_dict(self) -> dict[str, Any]:
        themes = []
        for componentsschemas_schema1201_item_data in self.themes:
            componentsschemas_schema1201_item = componentsschemas_schema1201_item_data.to_dict()
            themes.append(componentsschemas_schema1201_item)

        default_theme = self.default_theme

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "themes": themes,
                "defaultTheme": default_theme,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.artifact_theme_summary_dto import ArtifactThemeSummaryDto

        d = dict(src_dict)
        themes = []
        _themes = d.pop("themes")
        for componentsschemas_schema1201_item_data in _themes:
            componentsschemas_schema1201_item = ArtifactThemeSummaryDto.from_dict(
                componentsschemas_schema1201_item_data
            )

            themes.append(componentsschemas_schema1201_item)

        default_theme = d.pop("defaultTheme")

        list_artifact_themes_response = cls(
            themes=themes,
            default_theme=default_theme,
        )

        return list_artifact_themes_response
