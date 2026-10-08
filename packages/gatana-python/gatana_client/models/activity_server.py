from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ActivityServer")


@_attrs_define
class ActivityServer:
    """
    Attributes:
        server_id (str): ID of the server the calls went to
        slug (str): Slug of the server, as it reads on its page
        count (float): Tool calls made to that server
    """

    server_id: str
    slug: str
    count: float

    def to_dict(self) -> dict[str, Any]:
        server_id = self.server_id

        slug = self.slug

        count = self.count

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "serverId": server_id,
                "slug": slug,
                "count": count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        server_id = d.pop("serverId")

        slug = d.pop("slug")

        count = d.pop("count")

        activity_server = cls(
            server_id=server_id,
            slug=slug,
            count=count,
        )

        return activity_server
