from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailJmapConnection")


@_attrs_define
class EmailJmapConnection:
    """
    Attributes:
        protocol (Literal['jmap']): Protocol discriminator, always "jmap"
        session_url (Literal[''] | str | Unset):
        headers (list[list[str]] | Unset):
        account_id (None | str | Unset): ID of the JMAP account to use. Defaults to the primary mail account of the
            session
    """

    protocol: Literal["jmap"]
    session_url: Literal[""] | str | Unset = UNSET
    headers: list[list[str]] | Unset = UNSET
    account_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        protocol = self.protocol

        session_url: Literal[""] | str | Unset
        if isinstance(self.session_url, Unset):
            session_url = UNSET
        else:
            session_url = self.session_url

        headers: list[list[str]] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = []
            for componentsschemas_schema148_item_data in self.headers:
                componentsschemas_schema148_item = []
                for componentsschemas_schema148_item_item_data in componentsschemas_schema148_item_data:
                    componentsschemas_schema148_item_item: str
                    componentsschemas_schema148_item_item = componentsschemas_schema148_item_item_data
                    componentsschemas_schema148_item.append(componentsschemas_schema148_item_item)

                headers.append(componentsschemas_schema148_item)

        account_id: None | str | Unset
        if isinstance(self.account_id, Unset):
            account_id = UNSET
        else:
            account_id = self.account_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "protocol": protocol,
            }
        )
        if session_url is not UNSET:
            field_dict["sessionUrl"] = session_url
        if headers is not UNSET:
            field_dict["headers"] = headers
        if account_id is not UNSET:
            field_dict["accountId"] = account_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        protocol = cast(Literal["jmap"], d.pop("protocol"))
        if protocol != "jmap":
            raise ValueError(f"protocol must match const 'jmap', got '{protocol}'")

        def _parse_session_url(data: object) -> Literal[""] | str | Unset:
            if isinstance(data, Unset):
                return data
            componentsschemas_schema146_type_1 = cast(Literal[""], data)
            if componentsschemas_schema146_type_1 != "":
                raise ValueError(
                    f"/components/schemas/__schema146_type_1 must match const '', got '{componentsschemas_schema146_type_1}'"
                )
            return componentsschemas_schema146_type_1
            return cast(Literal[""] | str | Unset, data)

        session_url = _parse_session_url(d.pop("sessionUrl", UNSET))

        _headers = d.pop("headers", UNSET)
        headers: list[list[str]] | Unset = UNSET
        if _headers is not UNSET:
            headers = []
            for componentsschemas_schema148_item_data in _headers:
                componentsschemas_schema148_item = []
                _componentsschemas_schema148_item = componentsschemas_schema148_item_data
                for componentsschemas_schema148_item_item_data in _componentsschemas_schema148_item:

                    def _parse_componentsschemas_schema148_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema148_item_item = _parse_componentsschemas_schema148_item_item(
                        componentsschemas_schema148_item_item_data
                    )

                    componentsschemas_schema148_item.append(componentsschemas_schema148_item_item)

                headers.append(componentsschemas_schema148_item)

        def _parse_account_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        account_id = _parse_account_id(d.pop("accountId", UNSET))

        email_jmap_connection = cls(
            protocol=protocol,
            session_url=session_url,
            headers=headers,
            account_id=account_id,
        )

        email_jmap_connection.additional_properties = d
        return email_jmap_connection

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
