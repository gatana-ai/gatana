from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_1354 import Schema1354
from ..models.schema_1375 import Schema1375
from ..types import UNSET, Unset

T = TypeVar("T", bound="ArtifactContentResponse")


@_attrs_define
class ArtifactContentResponse:
    """
    Attributes:
        html (str): The served document: rendered to HTML when the version is Markdown, with the theme stylesheet linked
            in, as the content frame serves it
        content_type (Schema1375):
        version (float):
        title (str):
        visibility (Schema1354):
        theme (str): The theme the artifact is served with: 'gatana', 'none', or the id of an organization theme
        source (str | Unset):
    """

    html: str
    content_type: Schema1375
    version: float
    title: str
    visibility: Schema1354
    theme: str
    source: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        html = self.html

        content_type = self.content_type.value

        version = self.version

        title = self.title

        visibility = self.visibility.value

        theme = self.theme

        source = self.source

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "html": html,
                "contentType": content_type,
                "version": version,
                "title": title,
                "visibility": visibility,
                "theme": theme,
            }
        )
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        html = d.pop("html")

        content_type = Schema1375(d.pop("contentType"))

        version = d.pop("version")

        title = d.pop("title")

        visibility = Schema1354(d.pop("visibility"))

        theme = d.pop("theme")

        source = d.pop("source", UNSET)

        artifact_content_response = cls(
            html=html,
            content_type=content_type,
            version=version,
            title=title,
            visibility=visibility,
            theme=theme,
            source=source,
        )

        return artifact_content_response
