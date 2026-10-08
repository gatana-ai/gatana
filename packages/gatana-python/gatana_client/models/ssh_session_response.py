from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="SshSessionResponse")


@_attrs_define
class SshSessionResponse:
    """Short-lived JWT credential for SSH access to a sandbox

    Attributes:
        token (str):
        expires_in (float):
        host (str):
        port (float):
    """

    token: str
    expires_in: float
    host: str
    port: float

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        expires_in = self.expires_in

        host = self.host

        port = self.port

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "token": token,
                "expiresIn": expires_in,
                "host": host,
                "port": port,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        token = d.pop("token")

        expires_in = d.pop("expiresIn")

        host = d.pop("host")

        port = d.pop("port")

        ssh_session_response = cls(
            token=token,
            expires_in=expires_in,
            host=host,
            port=port,
        )

        return ssh_session_response
