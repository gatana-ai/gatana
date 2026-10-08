from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema497")


@_attrs_define
class Schema497:
    """
    Attributes:
        enabled (bool): Whether the server joins the tailnet
        auth_key (str): Tailscale auth key that registers the machine. It is spent at the first registration and the
            machine identity is kept across restarts, so use a tagged key and do not make it ephemeral
        hostname (None | str | Unset): Machine name on the tailnet. Defaults to gatana-<server slug>
    """

    enabled: bool
    auth_key: str
    hostname: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        auth_key = self.auth_key

        hostname: None | str | Unset
        if isinstance(self.hostname, Unset):
            hostname = UNSET
        else:
            hostname = self.hostname

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "enabled": enabled,
                "authKey": auth_key,
            }
        )
        if hostname is not UNSET:
            field_dict["hostname"] = hostname

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled")

        auth_key = d.pop("authKey")

        def _parse_hostname(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        hostname = _parse_hostname(d.pop("hostname", UNSET))

        schema_497 = cls(
            enabled=enabled,
            auth_key=auth_key,
            hostname=hostname,
        )

        return schema_497
