from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema79")


@_attrs_define
class Schema79:
    """
    Attributes:
        enabled (bool): Whether the health check is active
        delay_seconds (int | None): Seconds to wait before the first health check
        interval_seconds (int | None): Seconds between health checks
        failure_threshold (int | None): Number of consecutive failures before the process counts as unhealthy
        url (str | Unset):
    """

    enabled: bool
    delay_seconds: int | None
    interval_seconds: int | None
    failure_threshold: int | None
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        delay_seconds: int | None
        delay_seconds = self.delay_seconds

        interval_seconds: int | None
        interval_seconds = self.interval_seconds

        failure_threshold: int | None
        failure_threshold = self.failure_threshold

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enabled": enabled,
                "delaySeconds": delay_seconds,
                "intervalSeconds": interval_seconds,
                "failureThreshold": failure_threshold,
            }
        )
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled")

        def _parse_delay_seconds(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        delay_seconds = _parse_delay_seconds(d.pop("delaySeconds"))

        def _parse_interval_seconds(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        interval_seconds = _parse_interval_seconds(d.pop("intervalSeconds"))

        def _parse_failure_threshold(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        failure_threshold = _parse_failure_threshold(d.pop("failureThreshold"))

        url = d.pop("url", UNSET)

        schema_79 = cls(
            enabled=enabled,
            delay_seconds=delay_seconds,
            interval_seconds=interval_seconds,
            failure_threshold=failure_threshold,
            url=url,
        )

        schema_79.additional_properties = d
        return schema_79

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
