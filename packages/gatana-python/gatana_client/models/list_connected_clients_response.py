from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.connected_client import ConnectedClient


T = TypeVar("T", bound="ListConnectedClientsResponse")


@_attrs_define
class ListConnectedClientsResponse:
    """
    Attributes:
        clients (list[ConnectedClient]): Clients the signed-in user has authorized
    """

    clients: list[ConnectedClient]

    def to_dict(self) -> dict[str, Any]:
        clients = []
        for componentsschemas_schema1068_item_data in self.clients:
            componentsschemas_schema1068_item = componentsschemas_schema1068_item_data.to_dict()
            clients.append(componentsschemas_schema1068_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "clients": clients,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connected_client import ConnectedClient

        d = dict(src_dict)
        clients = []
        _clients = d.pop("clients")
        for componentsschemas_schema1068_item_data in _clients:
            componentsschemas_schema1068_item = ConnectedClient.from_dict(componentsschemas_schema1068_item_data)

            clients.append(componentsschemas_schema1068_item)

        list_connected_clients_response = cls(
            clients=clients,
        )

        return list_connected_clients_response
