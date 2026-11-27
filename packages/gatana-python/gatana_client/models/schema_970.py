from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_965 import Schema965
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_966 import Schema966
    from ..models.schema_967 import Schema967


T = TypeVar("T", bound="Schema970")


@_attrs_define
class Schema970:
    """
    Attributes:
        mode (Schema965 | Unset):
        actions (Schema966 | Unset): Actions for On mode. Missing targets use organization defaults or built-in values
        settings (Schema967 | Unset):
    """

    mode: Schema965 | Unset = UNSET
    actions: Schema966 | Unset = UNSET
    settings: Schema967 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        actions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        settings: dict[str, Any] | Unset = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode
        if actions is not UNSET:
            field_dict["actions"] = actions
        if settings is not UNSET:
            field_dict["settings"] = settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_966 import Schema966
        from ..models.schema_967 import Schema967

        d = dict(src_dict)
        _mode = d.pop("mode", UNSET)
        mode: Schema965 | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = Schema965(_mode)

        _actions = d.pop("actions", UNSET)
        actions: Schema966 | Unset
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = Schema966.from_dict(_actions)

        _settings = d.pop("settings", UNSET)
        settings: Schema967 | Unset
        if isinstance(_settings, Unset):
            settings = UNSET
        else:
            settings = Schema967.from_dict(_settings)

        schema_970 = cls(
            mode=mode,
            actions=actions,
            settings=settings,
        )

        return schema_970
