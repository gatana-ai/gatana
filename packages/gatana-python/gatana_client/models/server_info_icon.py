from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_786 import Schema786
from ..types import UNSET, Unset

T = TypeVar("T", bound="ServerInfoIcon")


@_attrs_define
class ServerInfoIcon:
    """
    Attributes:
        mime_type (str | Unset):
        sizes (list[str] | Unset):
        theme (Schema786 | Unset):
    """

    mime_type: str | Unset = UNSET
    sizes: list[str] | Unset = UNSET
    theme: Schema786 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        mime_type = self.mime_type

        sizes: list[str] | Unset = UNSET
        if not isinstance(self.sizes, Unset):
            sizes = self.sizes

        theme: str | Unset = UNSET
        if not isinstance(self.theme, Unset):
            theme = self.theme.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if mime_type is not UNSET:
            field_dict["mimeType"] = mime_type
        if sizes is not UNSET:
            field_dict["sizes"] = sizes
        if theme is not UNSET:
            field_dict["theme"] = theme

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mime_type = d.pop("mimeType", UNSET)

        sizes = cast(list[str], d.pop("sizes", UNSET))

        _theme = d.pop("theme", UNSET)
        theme: Schema786 | Unset
        if isinstance(_theme, Unset):
            theme = UNSET
        else:
            theme = Schema786(_theme)

        server_info_icon = cls(
            mime_type=mime_type,
            sizes=sizes,
            theme=theme,
        )

        return server_info_icon
