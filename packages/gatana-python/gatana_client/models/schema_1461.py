from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema1461")


@_attrs_define
class Schema1461:
    """
    Attributes:
        id (str):
        slug (str):
    """

    id: str
    slug: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        slug = self.slug

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "slug": slug,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        slug = d.pop("slug")

        schema_1461 = cls(
            id=id,
            slug=slug,
        )

        return schema_1461
