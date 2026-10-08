from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_541 import Schema541
    from ..models.schema_546 import Schema546


T = TypeVar("T", bound="ServerOAuthMetadata")


@_attrs_define
class ServerOAuthMetadata:
    """
    Attributes:
        resource (Schema541 | Unset):
        as_ (Schema546 | Unset):
    """

    resource: Schema541 | Unset = UNSET
    as_: Schema546 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        resource: dict[str, Any] | Unset = UNSET
        if not isinstance(self.resource, Unset):
            resource = self.resource.to_dict()

        as_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.as_, Unset):
            as_ = self.as_.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if resource is not UNSET:
            field_dict["resource"] = resource
        if as_ is not UNSET:
            field_dict["as"] = as_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_541 import Schema541
        from ..models.schema_546 import Schema546

        d = dict(src_dict)
        _resource = d.pop("resource", UNSET)
        resource: Schema541 | Unset
        if isinstance(_resource, Unset):
            resource = UNSET
        else:
            resource = Schema541.from_dict(_resource)

        _as_ = d.pop("as", UNSET)
        as_: Schema546 | Unset
        if isinstance(_as_, Unset):
            as_ = UNSET
        else:
            as_ = Schema546.from_dict(_as_)

        server_o_auth_metadata = cls(
            resource=resource,
            as_=as_,
        )

        return server_o_auth_metadata
