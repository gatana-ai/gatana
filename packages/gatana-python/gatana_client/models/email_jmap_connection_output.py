from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailJmapConnectionOutput")


@_attrs_define
class EmailJmapConnectionOutput:
    """
    Attributes:
        protocol (Literal['jmap']): Protocol discriminator, always "jmap"
        session_url (Literal[''] | str):
        headers (list[list[str]]):
        account_id (None | str | Unset): ID of the JMAP account to use. Defaults to the primary mail account of the
            session
    """

    protocol: Literal["jmap"]
    session_url: Literal[""] | str
    headers: list[list[str]]
    account_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        protocol = self.protocol

        session_url: Literal[""] | str
        session_url = self.session_url

        headers = []
        for componentsschemas_schema690_item_data in self.headers:
            componentsschemas_schema690_item = []
            for componentsschemas_schema690_item_item_data in componentsschemas_schema690_item_data:
                componentsschemas_schema690_item_item: str
                componentsschemas_schema690_item_item = componentsschemas_schema690_item_item_data
                componentsschemas_schema690_item.append(componentsschemas_schema690_item_item)

            headers.append(componentsschemas_schema690_item)

        account_id: None | str | Unset
        if isinstance(self.account_id, Unset):
            account_id = UNSET
        else:
            account_id = self.account_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "protocol": protocol,
                "sessionUrl": session_url,
                "headers": headers,
            }
        )
        if account_id is not UNSET:
            field_dict["accountId"] = account_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        protocol = cast(Literal["jmap"], d.pop("protocol"))
        if protocol != "jmap":
            raise ValueError(f"protocol must match const 'jmap', got '{protocol}'")

        def _parse_session_url(data: object) -> Literal[""] | str:
            componentsschemas_schema688_type_1 = cast(Literal[""], data)
            if componentsschemas_schema688_type_1 != "":
                raise ValueError(
                    f"/components/schemas/__schema688_type_1 must match const '', got '{componentsschemas_schema688_type_1}'"
                )
            return componentsschemas_schema688_type_1
            return cast(Literal[""] | str, data)

        session_url = _parse_session_url(d.pop("sessionUrl"))

        headers = []
        _headers = d.pop("headers")
        for componentsschemas_schema690_item_data in _headers:
            componentsschemas_schema690_item = []
            _componentsschemas_schema690_item = componentsschemas_schema690_item_data
            for componentsschemas_schema690_item_item_data in _componentsschemas_schema690_item:

                def _parse_componentsschemas_schema690_item_item(data: object) -> str:
                    return cast(str, data)

                componentsschemas_schema690_item_item = _parse_componentsschemas_schema690_item_item(
                    componentsschemas_schema690_item_item_data
                )

                componentsschemas_schema690_item.append(componentsschemas_schema690_item_item)

            headers.append(componentsschemas_schema690_item)

        def _parse_account_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        account_id = _parse_account_id(d.pop("accountId", UNSET))

        email_jmap_connection_output = cls(
            protocol=protocol,
            session_url=session_url,
            headers=headers,
            account_id=account_id,
        )

        return email_jmap_connection_output
