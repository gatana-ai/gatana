from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema486")


@_attrs_define
class Schema486:
    """
    Attributes:
        enabled (bool): Whether the health check is active
        url (str):
        delay_seconds (int | None): Seconds to wait before the first health check
        interval_seconds (int | None): Seconds between health checks
        failure_threshold (int | None): Number of consecutive failures before the process counts as unhealthy
    """

    enabled: bool
    url: str
    delay_seconds: int | None
    interval_seconds: int | None
    failure_threshold: int | None

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        url = self.url

        delay_seconds: int | None
        delay_seconds = self.delay_seconds

        interval_seconds: int | None
        interval_seconds = self.interval_seconds

        failure_threshold: int | None
        failure_threshold = self.failure_threshold

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "enabled": enabled,
                "url": url,
                "delaySeconds": delay_seconds,
                "intervalSeconds": interval_seconds,
                "failureThreshold": failure_threshold,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled")

        url = d.pop("url")

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

        schema_486 = cls(
            enabled=enabled,
            url=url,
            delay_seconds=delay_seconds,
            interval_seconds=interval_seconds,
            failure_threshold=failure_threshold,
        )

        return schema_486
