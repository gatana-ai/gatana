from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema93")


@_attrs_define
class Schema93:
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
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        auth_key = self.auth_key

        hostname: None | str | Unset
        if isinstance(self.hostname, Unset):
            hostname = UNSET
        else:
            hostname = self.hostname

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
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

        schema_93 = cls(
            enabled=enabled,
            auth_key=auth_key,
            hostname=hostname,
        )

        schema_93.additional_properties = d
        return schema_93

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
