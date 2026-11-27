from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_540 import Schema540
    from ..models.schema_850 import Schema850


T = TypeVar("T", bound="GetToolsSearchResponse200")


@_attrs_define
class GetToolsSearchResponse200:
    """
    Attributes:
        pagination (Schema540): Pagination metadata
        data (list[Schema850]): Items on the current page
    """

    pagination: Schema540
    data: list[Schema850]

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
        from ..models.schema_540 import Schema540
        from ..models.schema_850 import Schema850

        d = dict(src_dict)
        pagination = Schema540.from_dict(d.pop("pagination"))

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = Schema850.from_dict(data_item_data)

            data.append(data_item)

        get_tools_search_response_200 = cls(
            pagination=pagination,
            data=data,
        )

        return get_tools_search_response_200
