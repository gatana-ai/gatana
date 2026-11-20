from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_1393 import Schema1393

if TYPE_CHECKING:
    from ..models.schema_1456 import Schema1456
    from ..models.schema_1459 import Schema1459


T = TypeVar("T", bound="Schema1463")


@_attrs_define
class Schema1463:
    """
    Attributes:
        collection_id (str):
        collection_name (str):
        visibility (Schema1393):
        users (list[Schema1456]): User accounts with access, oldest share first
        teams (list[Schema1459]): Teams with access, oldest share first; every member of a team has it
    """

    collection_id: str
    collection_name: str
    visibility: Schema1393
    users: list[Schema1456]
    teams: list[Schema1459]

    def to_dict(self) -> dict[str, Any]:
        collection_id = self.collection_id

        collection_name = self.collection_name

        visibility = self.visibility.value

        users = []
        for componentsschemas_schema1455_item_data in self.users:
            componentsschemas_schema1455_item = componentsschemas_schema1455_item_data.to_dict()
            users.append(componentsschemas_schema1455_item)

        teams = []
        for componentsschemas_schema1458_item_data in self.teams:
            componentsschemas_schema1458_item = componentsschemas_schema1458_item_data.to_dict()
            teams.append(componentsschemas_schema1458_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "collectionId": collection_id,
                "collectionName": collection_name,
                "visibility": visibility,
                "users": users,
                "teams": teams,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1456 import Schema1456
        from ..models.schema_1459 import Schema1459

        d = dict(src_dict)
        collection_id = d.pop("collectionId")

        collection_name = d.pop("collectionName")

        visibility = Schema1393(d.pop("visibility"))

        users = []
        _users = d.pop("users")
        for componentsschemas_schema1455_item_data in _users:
            componentsschemas_schema1455_item = Schema1456.from_dict(componentsschemas_schema1455_item_data)

            users.append(componentsschemas_schema1455_item)

        teams = []
        _teams = d.pop("teams")
        for componentsschemas_schema1458_item_data in _teams:
            componentsschemas_schema1458_item = Schema1459.from_dict(componentsschemas_schema1458_item_data)

            teams.append(componentsschemas_schema1458_item)

        schema_1463 = cls(
            collection_id=collection_id,
            collection_name=collection_name,
            visibility=visibility,
            users=users,
            teams=teams,
        )

        return schema_1463
