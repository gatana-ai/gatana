from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="UploadSourceCodeResponse")



@_attrs_define
class UploadSourceCodeResponse:
    """ 
        Attributes:
            success (bool):
            message (str):
            analysis_result (Any | Unset):
     """

    success: bool
    message: str
    analysis_result: Any | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        analysis_result = self.analysis_result


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "success": success,
            "message": message,
        })
        if analysis_result is not UNSET:
            field_dict["analysisResult"] = analysis_result

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        analysis_result = d.pop("analysisResult", UNSET)

        upload_source_code_response = cls(
            success=success,
            message=message,
            analysis_result=analysis_result,
        )

        return upload_source_code_response

