from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_200 import Schema200
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_201 import Schema201
    from ..models.schema_204 import Schema204


T = TypeVar("T", bound="Schema199")


@_attrs_define
class Schema199:
    """
    Attributes:
        mode (Schema200):
        actions (Schema201 | Unset): Actions for On mode. Missing targets use organization defaults or built-in values
        settings (Schema204 | Unset):
    """

    mode: Schema200
    actions: Schema201 | Unset = UNSET
    settings: Schema204 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode.value

        actions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        settings: dict[str, Any] | Unset = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mode": mode,
            }
        )
        if actions is not UNSET:
            field_dict["actions"] = actions
        if settings is not UNSET:
            field_dict["settings"] = settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_201 import Schema201
        from ..models.schema_204 import Schema204

        d = dict(src_dict)
        mode = Schema200(d.pop("mode"))

        _actions = d.pop("actions", UNSET)
        actions: Schema201 | Unset
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = Schema201.from_dict(_actions)

        _settings = d.pop("settings", UNSET)
        settings: Schema204 | Unset
        if isinstance(_settings, Unset):
            settings = UNSET
        else:
            settings = Schema204.from_dict(_settings)

        schema_199 = cls(
            mode=mode,
            actions=actions,
            settings=settings,
        )

        schema_199.additional_properties = d
        return schema_199

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
