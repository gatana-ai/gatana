from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_764 import Schema764
from ..models.schema_765 import Schema765
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema966")


@_attrs_define
class Schema966:
    """Actions for On mode. Missing targets use organization defaults or built-in values

    Attributes:
        arguments (Schema764 | Unset):
        result (Schema765 | Unset):
    """

    arguments: Schema764 | Unset = UNSET
    result: Schema765 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        arguments: str | Unset = UNSET
        if not isinstance(self.arguments, Unset):
            arguments = self.arguments.value

        result: str | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if arguments is not UNSET:
            field_dict["arguments"] = arguments
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _arguments = d.pop("arguments", UNSET)
        arguments: Schema764 | Unset
        if isinstance(_arguments, Unset):
            arguments = UNSET
        else:
            arguments = Schema764(_arguments)

        _result = d.pop("result", UNSET)
        result: Schema765 | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = Schema765(_result)

        schema_966 = cls(
            arguments=arguments,
            result=result,
        )

        return schema_966
