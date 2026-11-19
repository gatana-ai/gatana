from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_683 import Schema683

T = TypeVar("T", bound="EmailSmtpServerOutput")


@_attrs_define
class EmailSmtpServerOutput:
    """SMTP server used to send mail. Uses the same credentials as IMAP

    Attributes:
        host (str): Host name of the SMTP server, for example smtp.gmail.com
        port (int):
        security (Schema683):
    """

    host: str
    port: int
    security: Schema683

    def to_dict(self) -> dict[str, Any]:
        host = self.host

        port = self.port

        security = self.security.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "host": host,
                "port": port,
                "security": security,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        host = d.pop("host")

        port = d.pop("port")

        security = Schema683(d.pop("security"))

        email_smtp_server_output = cls(
            host=host,
            port=port,
            security=security,
        )

        return email_smtp_server_output
