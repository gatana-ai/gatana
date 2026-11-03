from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_141 import Schema141
from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailSmtpServer")


@_attrs_define
class EmailSmtpServer:
    """SMTP server used to send mail. Uses the same credentials as IMAP

    Attributes:
        host (str): Host name of the SMTP server, for example smtp.gmail.com
        port (int | Unset):
        security (Schema141 | Unset):
    """

    host: str
    port: int | Unset = UNSET
    security: Schema141 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        host = self.host

        port = self.port

        security: str | Unset = UNSET
        if not isinstance(self.security, Unset):
            security = self.security.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "host": host,
            }
        )
        if port is not UNSET:
            field_dict["port"] = port
        if security is not UNSET:
            field_dict["security"] = security

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        host = d.pop("host")

        port = d.pop("port", UNSET)

        _security = d.pop("security", UNSET)
        security: Schema141 | Unset
        if isinstance(_security, Unset):
            security = UNSET
        else:
            security = Schema141(_security)

        email_smtp_server = cls(
            host=host,
            port=port,
            security=security,
        )

        email_smtp_server.additional_properties = d
        return email_smtp_server

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
