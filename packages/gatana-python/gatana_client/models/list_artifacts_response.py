from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.artifact_dto import ArtifactDto


T = TypeVar("T", bound="ListArtifactsResponse")


@_attrs_define
class ListArtifactsResponse:
    """
    Attributes:
        artifacts (list[ArtifactDto]):
    """

    artifacts: list[ArtifactDto]

    def to_dict(self) -> dict[str, Any]:
        artifacts = []
        for componentsschemas_schema1100_item_data in self.artifacts:
            componentsschemas_schema1100_item = componentsschemas_schema1100_item_data.to_dict()
            artifacts.append(componentsschemas_schema1100_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "artifacts": artifacts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.artifact_dto import ArtifactDto

        d = dict(src_dict)
        artifacts = []
        _artifacts = d.pop("artifacts")
        for componentsschemas_schema1100_item_data in _artifacts:
            componentsschemas_schema1100_item = ArtifactDto.from_dict(componentsschemas_schema1100_item_data)

            artifacts.append(componentsschemas_schema1100_item)

        list_artifacts_response = cls(
            artifacts=artifacts,
        )

        return list_artifacts_response
