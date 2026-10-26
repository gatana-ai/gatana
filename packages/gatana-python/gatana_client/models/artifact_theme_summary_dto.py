from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_1205 import Schema1205
from ..models.schema_1206 import Schema1206

T = TypeVar("T", bound="ArtifactThemeSummaryDto")


@_attrs_define
class ArtifactThemeSummaryDto:
    """
    Attributes:
        id (str):
        name (str):
        background_color (str): Lowercase hex color, #rrggbb
        text_color (str): Lowercase hex color, #rrggbb
        accent_color (str): Lowercase hex color, #rrggbb
        heading_font (Schema1205):
        body_font (Schema1205):
        code_font (Schema1206):
        created_at (str):
        updated_at (str):
        has_logo (bool): Whether the theme shows a logo at the top of the page
    """

    id: str
    name: str
    background_color: str
    text_color: str
    accent_color: str
    heading_font: Schema1205
    body_font: Schema1205
    code_font: Schema1206
    created_at: str
    updated_at: str
    has_logo: bool

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        background_color = self.background_color

        text_color = self.text_color

        accent_color = self.accent_color

        heading_font = self.heading_font.value

        body_font = self.body_font.value

        code_font = self.code_font.value

        created_at = self.created_at

        updated_at = self.updated_at

        has_logo = self.has_logo

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "backgroundColor": background_color,
                "textColor": text_color,
                "accentColor": accent_color,
                "headingFont": heading_font,
                "bodyFont": body_font,
                "codeFont": code_font,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "hasLogo": has_logo,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        background_color = d.pop("backgroundColor")

        text_color = d.pop("textColor")

        accent_color = d.pop("accentColor")

        heading_font = Schema1205(d.pop("headingFont"))

        body_font = Schema1205(d.pop("bodyFont"))

        code_font = Schema1206(d.pop("codeFont"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        has_logo = d.pop("hasLogo")

        artifact_theme_summary_dto = cls(
            id=id,
            name=name,
            background_color=background_color,
            text_color=text_color,
            accent_color=accent_color,
            heading_font=heading_font,
            body_font=body_font,
            code_font=code_font,
            created_at=created_at,
            updated_at=updated_at,
            has_logo=has_logo,
        )

        return artifact_theme_summary_dto
