from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.sandbox_dto import SandboxDto


T = TypeVar("T", bound="CreateSandboxResponse")


@_attrs_define
class CreateSandboxResponse:
    """
    Attributes:
        sandbox (SandboxDto):
    """

    sandbox: SandboxDto

    def to_dict(self) -> dict[str, Any]:
        sandbox = self.sandbox.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sandbox": sandbox,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sandbox_dto import SandboxDto

        d = dict(src_dict)
        sandbox = SandboxDto.from_dict(d.pop("sandbox"))

        create_sandbox_response = cls(
            sandbox=sandbox,
        )

        return create_sandbox_response
