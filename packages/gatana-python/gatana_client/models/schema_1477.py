from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema1477")


@_attrs_define
class Schema1477:
    """
    Attributes:
        id (str):
        slug (str):
        last_tool_refresh_at (None | str): Time of the last tool refresh, which also reads the skills
    """

    id: str
    slug: str
    last_tool_refresh_at: None | str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        slug = self.slug

        last_tool_refresh_at: None | str
        last_tool_refresh_at = self.last_tool_refresh_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "slug": slug,
                "lastToolRefreshAt": last_tool_refresh_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        slug = d.pop("slug")

        def _parse_last_tool_refresh_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_tool_refresh_at = _parse_last_tool_refresh_at(d.pop("lastToolRefreshAt"))

        schema_1477 = cls(
            id=id,
            slug=slug,
            last_tool_refresh_at=last_tool_refresh_at,
        )

        return schema_1477
