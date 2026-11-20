from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_758 import Schema758
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_759 import Schema759
    from ..models.schema_762 import Schema762


T = TypeVar("T", bound="ServerProtectionOutput")


@_attrs_define
class ServerProtectionOutput:
    """
    Attributes:
        mode (Schema758):
        settings (Schema762):
        actions (Schema759 | Unset): Actions for On mode. Missing targets use organization defaults or built-in values
    """

    mode: Schema758
    settings: Schema762
    actions: Schema759 | Unset = UNSET

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
        from ..models.schema_759 import Schema759
        from ..models.schema_762 import Schema762

        d = dict(src_dict)
        mode = Schema758(d.pop("mode"))

        settings = Schema762.from_dict(d.pop("settings"))

        _actions = d.pop("actions", UNSET)
        actions: Schema759 | Unset
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = Schema759.from_dict(_actions)

        server_protection_output = cls(
            mode=mode,
            settings=settings,
            actions=actions,
        )

        return server_protection_output
