from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_329 import Schema329
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateSkillBody")


@_attrs_define
class UpdateSkillBody:
    """
    Attributes:
        markdown (str | Unset): The whole skill as one SKILL.md document: a frontmatter block with name and description,
            then the instructions. The three fields are taken from it, so name, description and content are not given
            alongside
        name (str | Unset):
        description (str | Unset): One line saying when to use the skill, written for an agent deciding whether it
            applies
        content (str | Unset): The instructions as Markdown: the body of a SKILL.md without the frontmatter. Maximum 200
            KiB
        visibility (Schema329 | Unset):
        collection_id (None | str | Unset): ID of the collection to put the skill in, or null for a skill at root. You
            must be able to read the collection
    """

    markdown: str | Unset = UNSET
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    content: str | Unset = UNSET
    visibility: Schema329 | Unset = UNSET
    collection_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        markdown = self.markdown

        name = self.name

        description = self.description

        content = self.content

        visibility: str | Unset = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        collection_id: None | str | Unset
        if isinstance(self.collection_id, Unset):
            collection_id = UNSET
        else:
            collection_id = self.collection_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if markdown is not UNSET:
            field_dict["markdown"] = markdown
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if content is not UNSET:
            field_dict["content"] = content
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if collection_id is not UNSET:
            field_dict["collectionId"] = collection_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        markdown = d.pop("markdown", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        content = d.pop("content", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: Schema329 | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = Schema329(_visibility)

        def _parse_collection_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        collection_id = _parse_collection_id(d.pop("collectionId", UNSET))

        update_skill_body = cls(
            markdown=markdown,
            name=name,
            description=description,
            content=content,
            visibility=visibility,
            collection_id=collection_id,
        )

        update_skill_body.additional_properties = d
        return update_skill_body

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
