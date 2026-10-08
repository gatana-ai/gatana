from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_294 import Schema294
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateArtifactBody")


@_attrs_define
class CreateArtifactBody:
    """
    Attributes:
        title (str | Unset):
        html (str | Unset): A complete, self-contained HTML document. Give either html or markdown, not both
        markdown (str | Unset): A Markdown document (GitHub flavored). Stored as written and rendered to HTML when
            served. Give either html or markdown, not both
        theme (Schema294 | Unset): Stylesheet linked into the page when it is served. 'gatana' (the default) applies the
            Gatana fonts, colors and typography to plain HTML; 'none' serves the document as published
    """

    title: str | Unset = UNSET
    html: str | Unset = UNSET
    markdown: str | Unset = UNSET
    theme: Schema294 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        html = self.html

        markdown = self.markdown

        theme: str | Unset = UNSET
        if not isinstance(self.theme, Unset):
            theme = self.theme.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if html is not UNSET:
            field_dict["html"] = html
        if markdown is not UNSET:
            field_dict["markdown"] = markdown
        if theme is not UNSET:
            field_dict["theme"] = theme

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        html = d.pop("html", UNSET)

        markdown = d.pop("markdown", UNSET)

        _theme = d.pop("theme", UNSET)
        theme: Schema294 | Unset
        if isinstance(_theme, Unset):
            theme = UNSET
        else:
            theme = Schema294(_theme)

        create_artifact_body = cls(
            title=title,
            html=html,
            markdown=markdown,
            theme=theme,
        )

        create_artifact_body.additional_properties = d
        return create_artifact_body

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
