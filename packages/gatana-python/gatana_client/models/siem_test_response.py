from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="SiemTestResponse")


@_attrs_define
class SiemTestResponse:
    """
    Attributes:
        success (bool): Whether the destination accepted the test event
        status (float | None): HTTP status the receiver answered with, or null when the request never completed
        response_snippet (None | str): First part of the response body, to help a tenant debug a rejection
        error (None | str): Error message when the request failed, or null
        duration_ms (float): Duration of the test request in milliseconds
    """

    success: bool
    status: float | None
    response_snippet: None | str
    error: None | str
    duration_ms: float

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        status: float | None
        status = self.status

        response_snippet: None | str
        response_snippet = self.response_snippet

        error: None | str
        error = self.error

        duration_ms = self.duration_ms

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "success": success,
                "status": status,
                "responseSnippet": response_snippet,
                "error": error,
                "durationMs": duration_ms,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        def _parse_status(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        status = _parse_status(d.pop("status"))

        def _parse_response_snippet(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        response_snippet = _parse_response_snippet(d.pop("responseSnippet"))

        def _parse_error(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error = _parse_error(d.pop("error"))

        duration_ms = d.pop("durationMs")

        siem_test_response = cls(
            success=success,
            status=status,
            response_snippet=response_snippet,
            error=error,
            duration_ms=duration_ms,
        )

        return siem_test_response
