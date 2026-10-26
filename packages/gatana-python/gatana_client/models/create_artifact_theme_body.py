from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_340 import Schema340
from ..models.schema_343 import Schema343
from ..models.schema_345 import Schema345
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateArtifactThemeBody")


@_attrs_define
class CreateArtifactThemeBody:
    """
    Attributes:
        name (str): Name shown in pickers and accepted by agents; unique in the organization, not 'gatana' or 'none'
        background_color (str | Unset): Page background, as a hex color (#rgb or #rrggbb)
        text_color (str | Unset): Heading text; body text, lines and soft backgrounds are mixed from it and the
            background, as a hex color (#rgb or #rrggbb)
        accent_color (str | Unset): Buttons, links on hover, the eyebrow line and the gradient, as a hex color (#rgb or
            #rrggbb)
        heading_font (Schema340 | Unset):
        body_font (Schema343 | Unset):
        code_font (Schema345 | Unset): Font of code
        logo (str | Unset): Logo shown at the top of every page, as a base64 data: URL of a PNG, JPEG, WebP or SVG image
            of at most 256 KB, or an empty string for none
        extra_css (str | Unset): CSS added after the theme's own rules; the page's own styles still win over it
    """

    name: str
    background_color: str | Unset = UNSET
    text_color: str | Unset = UNSET
    accent_color: str | Unset = UNSET
    heading_font: Schema340 | Unset = UNSET
    body_font: Schema343 | Unset = UNSET
    code_font: Schema345 | Unset = UNSET
    logo: str | Unset = UNSET
    extra_css: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        background_color = self.background_color

        text_color = self.text_color

        accent_color = self.accent_color

        heading_font: str | Unset = UNSET
        if not isinstance(self.heading_font, Unset):
            heading_font = self.heading_font.value

        body_font: str | Unset = UNSET
        if not isinstance(self.body_font, Unset):
            body_font = self.body_font.value

        code_font: str | Unset = UNSET
        if not isinstance(self.code_font, Unset):
            code_font = self.code_font.value

        logo = self.logo

        extra_css = self.extra_css

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if background_color is not UNSET:
            field_dict["backgroundColor"] = background_color
        if text_color is not UNSET:
            field_dict["textColor"] = text_color
        if accent_color is not UNSET:
            field_dict["accentColor"] = accent_color
        if heading_font is not UNSET:
            field_dict["headingFont"] = heading_font
        if body_font is not UNSET:
            field_dict["bodyFont"] = body_font
        if code_font is not UNSET:
            field_dict["codeFont"] = code_font
        if logo is not UNSET:
            field_dict["logo"] = logo
        if extra_css is not UNSET:
            field_dict["extraCss"] = extra_css

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        background_color = d.pop("backgroundColor", UNSET)

        text_color = d.pop("textColor", UNSET)

        accent_color = d.pop("accentColor", UNSET)

        _heading_font = d.pop("headingFont", UNSET)
        heading_font: Schema340 | Unset
        if isinstance(_heading_font, Unset):
            heading_font = UNSET
        else:
            heading_font = Schema340(_heading_font)

        _body_font = d.pop("bodyFont", UNSET)
        body_font: Schema343 | Unset
        if isinstance(_body_font, Unset):
            body_font = UNSET
        else:
            body_font = Schema343(_body_font)

        _code_font = d.pop("codeFont", UNSET)
        code_font: Schema345 | Unset
        if isinstance(_code_font, Unset):
            code_font = UNSET
        else:
            code_font = Schema345(_code_font)

        logo = d.pop("logo", UNSET)

        extra_css = d.pop("extraCss", UNSET)

        create_artifact_theme_body = cls(
            name=name,
            background_color=background_color,
            text_color=text_color,
            accent_color=accent_color,
            heading_font=heading_font,
            body_font=body_font,
            code_font=code_font,
            logo=logo,
            extra_css=extra_css,
        )

        create_artifact_theme_body.additional_properties = d
        return create_artifact_theme_body

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
