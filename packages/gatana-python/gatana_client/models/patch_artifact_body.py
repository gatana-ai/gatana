from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_302 import Schema302
from ..models.schema_304 import Schema304
from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchArtifactBody")


@_attrs_define
class PatchArtifactBody:
    """
    Attributes:
        title (str | Unset):
        visibility (Schema302 | Unset):
        theme (Schema304 | Unset): Stylesheet linked into the page when it is served. 'gatana' (the default) applies the
            Gatana fonts, colors and typography to plain HTML; 'none' serves the document as published
    """

    title: str | Unset = UNSET
    visibility: Schema302 | Unset = UNSET
    theme: Schema304 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        visibility: str | Unset = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        theme: str | Unset = UNSET
        if not isinstance(self.theme, Unset):
            theme = self.theme.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if theme is not UNSET:
            field_dict["theme"] = theme

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: Schema302 | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = Schema302(_visibility)

        _theme = d.pop("theme", UNSET)
        theme: Schema304 | Unset
        if isinstance(_theme, Unset):
            theme = UNSET
        else:
            theme = Schema304(_theme)

        patch_artifact_body = cls(
            title=title,
            visibility=visibility,
            theme=theme,
        )

        patch_artifact_body.additional_properties = d
        return patch_artifact_body

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
