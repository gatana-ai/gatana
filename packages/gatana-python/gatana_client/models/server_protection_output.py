from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_755 import Schema755
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_756 import Schema756
    from ..models.schema_759 import Schema759


T = TypeVar("T", bound="ServerProtectionOutput")


@_attrs_define
class ServerProtectionOutput:
    """
    Attributes:
        mode (Schema755):
        settings (Schema759):
        actions (Schema756 | Unset): Actions for On mode. Missing targets use organization defaults or built-in values
    """

    mode: Schema755
    settings: Schema759
    actions: Schema756 | Unset = UNSET

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
        from ..models.schema_756 import Schema756
        from ..models.schema_759 import Schema759

        d = dict(src_dict)
        mode = Schema755(d.pop("mode"))

        settings = Schema759.from_dict(d.pop("settings"))

        _actions = d.pop("actions", UNSET)
        actions: Schema756 | Unset
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = Schema756.from_dict(_actions)

        server_protection_output = cls(
            mode=mode,
            settings=settings,
            actions=actions,
        )

        return server_protection_output
