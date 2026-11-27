from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_773 import Schema773
    from ..models.schema_777 import Schema777


T = TypeVar("T", bound="ResolvedProtection")


@_attrs_define
class ResolvedProtection:
    """
    Attributes:
        actions (Schema773): Actions for each supported target in On mode, regardless of the current mode
        settings (Schema777): The value and source of each option
    """

    actions: Schema773
    settings: Schema777

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
        from ..models.schema_773 import Schema773
        from ..models.schema_777 import Schema777

        d = dict(src_dict)
        actions = Schema773.from_dict(d.pop("actions"))

        settings = Schema777.from_dict(d.pop("settings"))

        resolved_protection = cls(
            actions=actions,
            settings=settings,
        )

        return resolved_protection
