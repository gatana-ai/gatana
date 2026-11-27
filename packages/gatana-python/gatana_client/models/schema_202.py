from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_203 import Schema203
from ..models.schema_204 import Schema204
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema202")


@_attrs_define
class Schema202:
    """Actions for On mode. Missing targets use organization defaults or built-in values

    Attributes:
        arguments (Schema203 | Unset):
        result (Schema204 | Unset):
    """

    arguments: Schema203 | Unset = UNSET
    result: Schema204 | Unset = UNSET

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
        arguments: Schema203 | Unset
        if isinstance(_arguments, Unset):
            arguments = UNSET
        else:
            arguments = Schema203(_arguments)

        _result = d.pop("result", UNSET)
        result: Schema204 | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = Schema204(_result)

        schema_202 = cls(
            arguments=arguments,
            result=result,
        )

        return schema_202
