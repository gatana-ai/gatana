from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_122_as_type_0 import Schema122AsType0
    from ..models.schema_122_resource_type_0 import Schema122ResourceType0


T = TypeVar("T", bound="Schema122")


@_attrs_define
class Schema122:
    """
    Attributes:
        resource (None | Schema122ResourceType0 | Unset):
        as_ (None | Schema122AsType0 | Unset):
    """

    resource: None | Schema122ResourceType0 | Unset = UNSET
    as_: None | Schema122AsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_122_as_type_0 import Schema122AsType0
        from ..models.schema_122_resource_type_0 import Schema122ResourceType0

        resource: dict[str, Any] | None | Unset
        if isinstance(self.resource, Unset):
            resource = UNSET
        elif isinstance(self.resource, Schema122ResourceType0):
            resource = self.resource.to_dict()
        else:
            resource = self.resource

        as_: dict[str, Any] | None | Unset
        if isinstance(self.as_, Unset):
            as_ = UNSET
        elif isinstance(self.as_, Schema122AsType0):
            as_ = self.as_.to_dict()
        else:
            as_ = self.as_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if resource is not UNSET:
            field_dict["resource"] = resource
        if as_ is not UNSET:
            field_dict["as"] = as_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_122_as_type_0 import Schema122AsType0
        from ..models.schema_122_resource_type_0 import Schema122ResourceType0

        d = dict(src_dict)

        def _parse_resource(data: object) -> None | Schema122ResourceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                resource_type_0 = Schema122ResourceType0.from_dict(data)

                return resource_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema122ResourceType0 | Unset, data)

        resource = _parse_resource(d.pop("resource", UNSET))

        def _parse_as_(data: object) -> None | Schema122AsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                as_type_0 = Schema122AsType0.from_dict(data)

                return as_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema122AsType0 | Unset, data)

        as_ = _parse_as_(d.pop("as", UNSET))

        schema_122 = cls(
            resource=resource,
            as_=as_,
        )

        schema_122.additional_properties = d
        return schema_122

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
