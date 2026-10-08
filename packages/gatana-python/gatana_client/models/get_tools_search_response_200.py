from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_410 import Schema410
    from ..models.schema_627 import Schema627


T = TypeVar("T", bound="GetToolsSearchResponse200")


@_attrs_define
class GetToolsSearchResponse200:
    """
    Attributes:
        pagination (Schema410): Pagination metadata
        data (list[Schema627]): Items on the current page
    """

    pagination: Schema410
    data: list[Schema627]

    def to_dict(self) -> dict[str, Any]:
        pagination = self.pagination.to_dict()

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "pagination": pagination,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_410 import Schema410
        from ..models.schema_627 import Schema627

        d = dict(src_dict)
        pagination = Schema410.from_dict(d.pop("pagination"))

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = Schema627.from_dict(data_item_data)

            data.append(data_item)

        get_tools_search_response_200 = cls(
            pagination=pagination,
            data=data,
        )

        return get_tools_search_response_200
