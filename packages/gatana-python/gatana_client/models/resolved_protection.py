from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_766 import Schema766
    from ..models.schema_770 import Schema770


T = TypeVar("T", bound="ResolvedProtection")


@_attrs_define
class ResolvedProtection:
    """
    Attributes:
        actions (Schema766): Actions for each supported target in On mode, regardless of the current mode
        settings (Schema770): The value and source of each option
    """

    actions: Schema766
    settings: Schema770

    def to_dict(self) -> dict[str, Any]:
        actions = self.actions.to_dict()

        settings = self.settings.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "actions": actions,
                "settings": settings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_766 import Schema766
        from ..models.schema_770 import Schema770

        d = dict(src_dict)
        actions = Schema766.from_dict(d.pop("actions"))

        settings = Schema770.from_dict(d.pop("settings"))

        resolved_protection = cls(
            actions=actions,
            settings=settings,
        )

        return resolved_protection
