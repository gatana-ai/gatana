from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_762 import Schema762
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_763 import Schema763
    from ..models.schema_766 import Schema766


T = TypeVar("T", bound="Schema761")


@_attrs_define
class Schema761:
    """
    Attributes:
        mode (Schema762):
        settings (Schema766):
        actions (Schema763 | Unset): Actions for On mode. Missing targets use organization defaults or built-in values
    """

    mode: Schema762
    settings: Schema766
    actions: Schema763 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode.value

        settings = self.settings.to_dict()

        actions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mode": mode,
                "settings": settings,
            }
        )
        if actions is not UNSET:
            field_dict["actions"] = actions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_763 import Schema763
        from ..models.schema_766 import Schema766

        d = dict(src_dict)
        mode = Schema762(d.pop("mode"))

        settings = Schema766.from_dict(d.pop("settings"))

        _actions = d.pop("actions", UNSET)
        actions: Schema763 | Unset
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = Schema763.from_dict(_actions)

        schema_761 = cls(
            mode=mode,
            settings=settings,
            actions=actions,
        )

        return schema_761
