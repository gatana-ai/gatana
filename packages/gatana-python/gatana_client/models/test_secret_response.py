from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="TestSecretResponse")



@_attrs_define
class TestSecretResponse:
    """ 
        Attributes:
            success (bool):
            message (str):
            value (str | Unset):
     """

    success: bool
    message: str
    value: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        value = self.value


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "success": success,
            "message": message,
        })
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        value = d.pop("value", UNSET)

        test_secret_response = cls(
            success=success,
            message=message,
            value=value,
        )

        return test_secret_response

