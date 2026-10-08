from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1084 import Schema1084


T = TypeVar("T", bound="UpdateConnectedClientResponse")


@_attrs_define
class UpdateConnectedClientResponse:
    """
    Attributes:
        client (Schema1084):
    """

    client: Schema1084

    def to_dict(self) -> dict[str, Any]:
        client = self.client.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "client": client,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1084 import Schema1084

        d = dict(src_dict)
        client = Schema1084.from_dict(d.pop("client"))

        update_connected_client_response = cls(
            client=client,
        )

        return update_connected_client_response
