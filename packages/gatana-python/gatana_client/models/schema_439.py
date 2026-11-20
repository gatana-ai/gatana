from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_439_encoding import Schema439Encoding

T = TypeVar("T", bound="Schema439")


@_attrs_define
class Schema439:
    """
    Attributes:
        path (str): Path relative to the skill folder. Use / as the separator, without "." or ".." segments. Maximum 255
            bytes. "SKILL.md" is the skill document
        encoding (Schema439Encoding): How content holds the bytes of the file
        content (str):
    """

    path: str
    encoding: Schema439Encoding
    content: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        encoding = self.encoding.value

        content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "encoding": encoding,
                "content": content,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        encoding = Schema439Encoding(d.pop("encoding"))

        content = d.pop("content")

        schema_439 = cls(
            path=path,
            encoding=encoding,
            content=content,
        )

        schema_439.additional_properties = d
        return schema_439

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
