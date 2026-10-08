from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_1105 import Schema1105

T = TypeVar("T", bound="ArtifactVersionMetaDto")


@_attrs_define
class ArtifactVersionMetaDto:
    """
    Attributes:
        version (float):
        size_bytes (float):
        content_type (Schema1105):
        created_by_user_id (str):
        created_at (str):
    """

    version: float
    size_bytes: float
    content_type: Schema1105
    created_by_user_id: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        size_bytes = self.size_bytes

        content_type = self.content_type.value

        created_by_user_id = self.created_by_user_id

        created_at = self.created_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "version": version,
                "sizeBytes": size_bytes,
                "contentType": content_type,
                "createdByUserId": created_by_user_id,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version = d.pop("version")

        size_bytes = d.pop("sizeBytes")

        content_type = Schema1105(d.pop("contentType"))

        created_by_user_id = d.pop("createdByUserId")

        created_at = d.pop("createdAt")

        artifact_version_meta_dto = cls(
            version=version,
            size_bytes=size_bytes,
            content_type=content_type,
            created_by_user_id=created_by_user_id,
            created_at=created_at,
        )

        return artifact_version_meta_dto
