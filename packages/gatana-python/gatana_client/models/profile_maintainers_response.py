from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1107 import Schema1107


T = TypeVar("T", bound="ProfileMaintainersResponse")


@_attrs_define
class ProfileMaintainersResponse:
    """
    Attributes:
        maintainers (list[Schema1107]): Users who maintain the profile
    """

    maintainers: list[Schema1107]

    def to_dict(self) -> dict[str, Any]:
        maintainers = []
        for componentsschemas_schema1106_item_data in self.maintainers:
            componentsschemas_schema1106_item = componentsschemas_schema1106_item_data.to_dict()
            maintainers.append(componentsschemas_schema1106_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "maintainers": maintainers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1107 import Schema1107

        d = dict(src_dict)
        maintainers = []
        _maintainers = d.pop("maintainers")
        for componentsschemas_schema1106_item_data in _maintainers:
            componentsschemas_schema1106_item = Schema1107.from_dict(componentsschemas_schema1106_item_data)

            maintainers.append(componentsschemas_schema1106_item)

        profile_maintainers_response = cls(
            maintainers=maintainers,
        )

        return profile_maintainers_response
