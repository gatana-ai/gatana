from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PreviewArtifactThemeResponse")


@_attrs_define
class PreviewArtifactThemeResponse:
    """
    Attributes:
        html (str): A sample Markdown document rendered and styled with the given theme, as one document with the
            stylesheet inlined. Render it in a sandboxed frame that allows scripts: it takes a later stylesheet from a
            message {type: "artifact-theme-css", css} of the embedding page
        css (str): The stylesheet of the given theme, as inlined in html; post it to a preview already shown to restyle
            it in place
    """

    html: str
    css: str

    def to_dict(self) -> dict[str, Any]:
        html = self.html

        css = self.css

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "html": html,
                "css": css,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        html = d.pop("html")

        css = d.pop("css")

        preview_artifact_theme_response = cls(
            html=html,
            css=css,
        )

        return preview_artifact_theme_response
