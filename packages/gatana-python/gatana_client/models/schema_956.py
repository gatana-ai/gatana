from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_760 import Schema760
from ..models.schema_761 import Schema761
from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema956")


@_attrs_define
class Schema956:
    """Actions for On mode. Missing targets use organization defaults or built-in values

    Attributes:
        arguments (Schema760 | Unset):
        result (Schema761 | Unset):
    """

    arguments: Schema760 | Unset = UNSET
    result: Schema761 | Unset = UNSET

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
        arguments: Schema760 | Unset
        if isinstance(_arguments, Unset):
            arguments = UNSET
        else:
            arguments = Schema760(_arguments)

        _result = d.pop("result", UNSET)
        result: Schema761 | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = Schema761(_result)

        schema_956 = cls(
            arguments=arguments,
            result=result,
        )

        return schema_956
