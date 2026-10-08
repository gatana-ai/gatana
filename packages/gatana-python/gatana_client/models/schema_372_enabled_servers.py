from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Schema372EnabledServers")


@_attrs_define
class Schema372EnabledServers:
    """
    Attributes:
        quota (float):
        current (float):
        remaining (float):
    """

    quota: float
    current: float
    remaining: float

    def to_dict(self) -> dict[str, Any]:
        quota = self.quota

        current = self.current

        remaining = self.remaining

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "quota": quota,
                "current": current,
                "remaining": remaining,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        quota = d.pop("quota")

        current = d.pop("current")

        remaining = d.pop("remaining")

        schema_372_enabled_servers = cls(
            quota=quota,
            current=current,
            remaining=remaining,
        )

        return schema_372_enabled_servers
