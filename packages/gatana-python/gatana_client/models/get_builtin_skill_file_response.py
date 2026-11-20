from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1492 import Schema1492


T = TypeVar("T", bound="GetBuiltinSkillFileResponse")


@_attrs_define
class GetBuiltinSkillFileResponse:
    """
    Attributes:
        file (Schema1492):
    """

    file: Schema1492

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "file": file,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1492 import Schema1492

        d = dict(src_dict)
        file = Schema1492.from_dict(d.pop("file"))

        get_builtin_skill_file_response = cls(
            file=file,
        )

        return get_builtin_skill_file_response
