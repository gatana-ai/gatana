from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1462 import Schema1462


T = TypeVar("T", bound="GetSkillFileResponse")


@_attrs_define
class GetSkillFileResponse:
    """
    Attributes:
        file (Schema1462):
    """

    file: Schema1462

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
        from ..models.schema_1462 import Schema1462

        d = dict(src_dict)
        file = Schema1462.from_dict(d.pop("file"))

        get_skill_file_response = cls(
            file=file,
        )

        return get_skill_file_response
