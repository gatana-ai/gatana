from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1497 import Schema1497


T = TypeVar("T", bound="Schema1496")


@_attrs_define
class Schema1496:
    """
    Attributes:
        uri (str): Page URI published by the MCP server
        html (str): Unscanned HTML from the MCP server
        meta (None | Schema1497): Page metadata from the MCP server, including network access, permissions and border
            preferences
    """

    uri: str
    html: str
    meta: None | Schema1497

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1497 import Schema1497

        uri = self.uri

        html = self.html

        meta: dict[str, Any] | None
        if isinstance(self.meta, Schema1497):
            meta = self.meta.to_dict()
        else:
            meta = self.meta

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "uri": uri,
                "html": html,
                "meta": meta,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1497 import Schema1497

        d = dict(src_dict)
        uri = d.pop("uri")

        html = d.pop("html")

        def _parse_meta(data: object) -> None | Schema1497:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                meta_type_0 = Schema1497.from_dict(data)

                return meta_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1497, data)

        meta = _parse_meta(d.pop("meta"))

        schema_1496 = cls(
            uri=uri,
            html=html,
            meta=meta,
        )

        return schema_1496
