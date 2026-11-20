from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_770 import Schema770
    from ..models.schema_772 import Schema772


T = TypeVar("T", bound="Schema769")


@_attrs_define
class Schema769:
    """Actions for each supported target in On mode, regardless of the current mode

    Attributes:
        arguments (Schema770 | Unset):
        result (Schema772 | Unset):
    """

    arguments: Schema770 | Unset = UNSET
    result: Schema772 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        arguments: dict[str, Any] | Unset = UNSET
        if not isinstance(self.arguments, Unset):
            arguments = self.arguments.to_dict()

        result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if arguments is not UNSET:
            field_dict["arguments"] = arguments
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_770 import Schema770
        from ..models.schema_772 import Schema772

        d = dict(src_dict)
        _arguments = d.pop("arguments", UNSET)
        arguments: Schema770 | Unset
        if isinstance(_arguments, Unset):
            arguments = UNSET
        else:
            arguments = Schema770.from_dict(_arguments)

        _result = d.pop("result", UNSET)
        result: Schema772 | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = Schema772.from_dict(_result)

        schema_769 = cls(
            arguments=arguments,
            result=result,
        )

        return schema_769
