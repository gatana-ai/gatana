from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_1463 import Schema1463

T = TypeVar("T", bound="Schema1508")


@_attrs_define
class Schema1508:
    """
    Attributes:
        path (str): Path in the skill folder, with / as the separator, e.g. "SKILL.md"
        size_bytes (float):
        digest (str): SHA-256 digest of the file, as "sha256:<hex>"
        mime_type (str): Set by Gatana from the file extension
        encoding (Schema1463): base64 when the bytes are not valid UTF-8
        content (str):
        uri (str): File URI for agents to use through Gatana
    """

    path: str
    size_bytes: float
    digest: str
    mime_type: str
    encoding: Schema1463
    content: str
    uri: str

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        size_bytes = self.size_bytes

        digest = self.digest

        mime_type = self.mime_type

        encoding = self.encoding.value

        content = self.content

        uri = self.uri

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "path": path,
                "sizeBytes": size_bytes,
                "digest": digest,
                "mimeType": mime_type,
                "encoding": encoding,
                "content": content,
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

        encoding = Schema1463(d.pop("encoding"))

        content = d.pop("content")

        uri = d.pop("uri")

        schema_1508 = cls(
            path=path,
            size_bytes=size_bytes,
            digest=digest,
            mime_type=mime_type,
            encoding=encoding,
            content=content,
            uri=uri,
        )

        return schema_1508
