from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_676 import Schema676

if TYPE_CHECKING:
    from ..models.email_smtp_server_output import EmailSmtpServerOutput


T = TypeVar("T", bound="EmailImapConnectionOutput")


@_attrs_define
class EmailImapConnectionOutput:
    """
    Attributes:
        protocol (Literal['imap']): Protocol discriminator, always "imap"
        host (str):
        port (int):
        security (Schema676):
        username (str):
        password (str):
        smtp (EmailSmtpServerOutput | None):
        save_sent_copy (bool):
    """

    protocol: Literal["imap"]
    host: str
    port: int
    security: Schema676
    username: str
    password: str
    smtp: EmailSmtpServerOutput | None
    save_sent_copy: bool

    def to_dict(self) -> dict[str, Any]:
        from ..models.email_smtp_server_output import EmailSmtpServerOutput

        protocol = self.protocol

        host = self.host

        port = self.port

        security = self.security.value

        username = self.username

        password = self.password

        smtp: dict[str, Any] | None
        if isinstance(self.smtp, EmailSmtpServerOutput):
            smtp = self.smtp.to_dict()
        else:
            smtp = self.smtp

        save_sent_copy = self.save_sent_copy

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "protocol": protocol,
                "host": host,
                "port": port,
                "security": security,
                "username": username,
                "password": password,
                "smtp": smtp,
                "saveSentCopy": save_sent_copy,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_smtp_server_output import EmailSmtpServerOutput

        d = dict(src_dict)
        protocol = cast(Literal["imap"], d.pop("protocol"))
        if protocol != "imap":
            raise ValueError(f"protocol must match const 'imap', got '{protocol}'")

        host = d.pop("host")

        port = d.pop("port")

        security = Schema676(d.pop("security"))

        username = d.pop("username")

        password = d.pop("password")

        def _parse_smtp(data: object) -> EmailSmtpServerOutput | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema682_type_0 = EmailSmtpServerOutput.from_dict(data)

                return componentsschemas_schema682_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EmailSmtpServerOutput | None, data)

        smtp = _parse_smtp(d.pop("smtp"))

        save_sent_copy = d.pop("saveSentCopy")

        email_imap_connection_output = cls(
            protocol=protocol,
            host=host,
            port=port,
            security=security,
            username=username,
            password=password,
            smtp=smtp,
            save_sent_copy=save_sent_copy,
        )

        return email_imap_connection_output
