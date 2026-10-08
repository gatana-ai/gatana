from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.skill_collection_dto import SkillCollectionDto


T = TypeVar("T", bound="ListSkillCollectionsResponse")


@_attrs_define
class ListSkillCollectionsResponse:
    """
    Attributes:
        collections (list[SkillCollectionDto]):
    """

    collections: list[SkillCollectionDto]

    def to_dict(self) -> dict[str, Any]:
        collections = []
        for componentsschemas_schema1180_item_data in self.collections:
            componentsschemas_schema1180_item = componentsschemas_schema1180_item_data.to_dict()
            collections.append(componentsschemas_schema1180_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "collections": collections,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.skill_collection_dto import SkillCollectionDto

        d = dict(src_dict)
        collections = []
        _collections = d.pop("collections")
        for componentsschemas_schema1180_item_data in _collections:
            componentsschemas_schema1180_item = SkillCollectionDto.from_dict(componentsschemas_schema1180_item_data)

            collections.append(componentsschemas_schema1180_item)

        list_skill_collections_response = cls(
            collections=collections,
        )

        return list_skill_collections_response
