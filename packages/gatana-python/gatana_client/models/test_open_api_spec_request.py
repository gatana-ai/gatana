from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_161 import Schema161
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_162 import Schema162


T = TypeVar("T", bound="TestOpenApiSpecRequest")


@_attrs_define
class TestOpenApiSpecRequest:
    """
    Attributes:
        method (Schema161): Whether to test a spec string or a spec URL.
        headers (Schema162 | Unset):
        spec (str | Unset):
        spec_url (str | Unset):
    """

    method: Schema161
    headers: Schema162 | Unset = UNSET
    spec: str | Unset = UNSET
    spec_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        method = self.method.value

        headers: dict[str, Any] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        spec = self.spec

        spec_url = self.spec_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "method": method,
            }
        )
        if headers is not UNSET:
            field_dict["headers"] = headers
        if spec is not UNSET:
            field_dict["spec"] = spec
        if spec_url is not UNSET:
            field_dict["specUrl"] = spec_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_162 import Schema162

        d = dict(src_dict)
        method = Schema161(d.pop("method"))

        _headers = d.pop("headers", UNSET)
        headers: Schema162 | Unset
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = Schema162.from_dict(_headers)

        spec = d.pop("spec", UNSET)

        spec_url = d.pop("specUrl", UNSET)

        test_open_api_spec_request = cls(
            method=method,
            headers=headers,
            spec=spec,
            spec_url=spec_url,
        )

        test_open_api_spec_request.additional_properties = d
        return test_open_api_spec_request

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
