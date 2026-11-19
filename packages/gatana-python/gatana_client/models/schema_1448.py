from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema1448")


@_attrs_define
class Schema1448:
    """
    Attributes:
        path (str): File path in the skill folder, as written in the URI
        size_bytes (float):
        digest (str): SHA-256 digest of the file, as "sha256:<hex>"
        mime_type (str): Set by Gatana from the file extension
        uri (str): URI of the file as the server publishes it
    """

    path: str
    size_bytes: float
    digest: str
    mime_type: str
    uri: str

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        size_bytes = self.size_bytes

        digest = self.digest

        mime_type = self.mime_type

        uri = self.uri

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "path": path,
                "sizeBytes": size_bytes,
                "digest": digest,
                "mimeType": mime_type,
                "uri": uri,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        size_bytes = d.pop("sizeBytes")

        digest = d.pop("digest")

        mime_type = d.pop("mimeType")

        uri = d.pop("uri")

        schema_1448 = cls(
            path=path,
            size_bytes=size_bytes,
            digest=digest,
            mime_type=mime_type,
            uri=uri,
        )

        return schema_1448
