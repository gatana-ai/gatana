from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_130 import Schema130
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_smtp_server import EmailSmtpServer


T = TypeVar("T", bound="EmailImapConnection")


@_attrs_define
class EmailImapConnection:
    """
    Attributes:
        protocol (Literal['imap']): Protocol discriminator, always "imap"
        host (str | Unset):
        port (int | Unset):
        security (Schema130 | Unset):
        username (str | Unset):
        password (str | Unset):
        smtp (EmailSmtpServer | None | Unset):
        save_sent_copy (bool | Unset):
    """

    protocol: Literal["imap"]
    host: str | Unset = UNSET
    port: int | Unset = UNSET
    security: Schema130 | Unset = UNSET
    username: str | Unset = UNSET
    password: str | Unset = UNSET
    smtp: EmailSmtpServer | None | Unset = UNSET
    save_sent_copy: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.email_smtp_server import EmailSmtpServer

        protocol = self.protocol

        host = self.host

        port = self.port

        security: str | Unset = UNSET
        if not isinstance(self.security, Unset):
            security = self.security.value

        username = self.username

        password = self.password

        smtp: dict[str, Any] | None | Unset
        if isinstance(self.smtp, Unset):
            smtp = UNSET
        elif isinstance(self.smtp, EmailSmtpServer):
            smtp = self.smtp.to_dict()
        else:
            smtp = self.smtp

        save_sent_copy = self.save_sent_copy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "protocol": protocol,
            }
        )
        if host is not UNSET:
            field_dict["host"] = host
        if port is not UNSET:
            field_dict["port"] = port
        if security is not UNSET:
            field_dict["security"] = security
        if username is not UNSET:
            field_dict["username"] = username
        if password is not UNSET:
            field_dict["password"] = password
        if smtp is not UNSET:
            field_dict["smtp"] = smtp
        if save_sent_copy is not UNSET:
            field_dict["saveSentCopy"] = save_sent_copy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_smtp_server import EmailSmtpServer

        d = dict(src_dict)
        protocol = cast(Literal["imap"], d.pop("protocol"))
        if protocol != "imap":
            raise ValueError(f"protocol must match const 'imap', got '{protocol}'")

        host = d.pop("host", UNSET)

        port = d.pop("port", UNSET)

        _security = d.pop("security", UNSET)
        security: Schema130 | Unset
        if isinstance(_security, Unset):
            security = UNSET
        else:
            security = Schema130(_security)

        username = d.pop("username", UNSET)

        password = d.pop("password", UNSET)

        def _parse_smtp(data: object) -> EmailSmtpServer | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema136_type_0 = EmailSmtpServer.from_dict(data)

                return componentsschemas_schema136_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EmailSmtpServer | None | Unset, data)

        smtp = _parse_smtp(d.pop("smtp", UNSET))

        save_sent_copy = d.pop("saveSentCopy", UNSET)

        email_imap_connection = cls(
            protocol=protocol,
            host=host,
            port=port,
            security=security,
            username=username,
            password=password,
            smtp=smtp,
            save_sent_copy=save_sent_copy,
        )

        email_imap_connection.additional_properties = d
        return email_imap_connection

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
