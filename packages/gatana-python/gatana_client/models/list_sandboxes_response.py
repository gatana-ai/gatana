from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.sandbox_dto import SandboxDto


T = TypeVar("T", bound="ListSandboxesResponse")


@_attrs_define
class ListSandboxesResponse:
    """
    Attributes:
        sandboxes (list[SandboxDto]):
    """

    sandboxes: list[SandboxDto]

    def to_dict(self) -> dict[str, Any]:
        sandboxes = []
        for componentsschemas_schema1041_item_data in self.sandboxes:
            componentsschemas_schema1041_item = componentsschemas_schema1041_item_data.to_dict()
            sandboxes.append(componentsschemas_schema1041_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sandboxes": sandboxes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sandbox_dto import SandboxDto

        d = dict(src_dict)
        sandboxes = []
        _sandboxes = d.pop("sandboxes")
        for componentsschemas_schema1041_item_data in _sandboxes:
            componentsschemas_schema1041_item = SandboxDto.from_dict(componentsschemas_schema1041_item_data)

            sandboxes.append(componentsschemas_schema1041_item)

        list_sandboxes_response = cls(
            sandboxes=sandboxes,
        )

        return list_sandboxes_response
