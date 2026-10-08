from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_338 import Schema338
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSkillCollectionBody")


@_attrs_define
class CreateSkillCollectionBody:
    """
    Attributes:
        name (str):
        description (str | Unset): One line saying what the collection gathers
        visibility (Schema338 | Unset):
    """

    name: str
    description: str | Unset = UNSET
    visibility: Schema338 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        visibility: str | Unset = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: Schema338 | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = Schema338(_visibility)

        create_skill_collection_body = cls(
            name=name,
            description=description,
            visibility=visibility,
        )

        create_skill_collection_body.additional_properties = d
        return create_skill_collection_body

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
