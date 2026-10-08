from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.siem_destination_response import SiemDestinationResponse


T = TypeVar("T", bound="SiemDestinationDetailResponse")


@_attrs_define
class SiemDestinationDetailResponse:
    """
    Attributes:
        destination (None | SiemDestinationResponse): The SIEM destination, or null when none is configured
    """

    destination: None | SiemDestinationResponse

    def to_dict(self) -> dict[str, Any]:
        from ..models.siem_destination_response import SiemDestinationResponse

        destination: dict[str, Any] | None
        if isinstance(self.destination, SiemDestinationResponse):
            destination = self.destination.to_dict()
        else:
            destination = self.destination

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "destination": destination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.siem_destination_response import SiemDestinationResponse

        d = dict(src_dict)

        def _parse_destination(data: object) -> None | SiemDestinationResponse:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema959_type_0 = SiemDestinationResponse.from_dict(data)

                return componentsschemas_schema959_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SiemDestinationResponse, data)

        destination = _parse_destination(d.pop("destination"))

        siem_destination_detail_response = cls(
            destination=destination,
        )

        return siem_destination_detail_response
