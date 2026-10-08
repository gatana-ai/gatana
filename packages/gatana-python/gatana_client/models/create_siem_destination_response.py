from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_983 import Schema983


T = TypeVar("T", bound="CreateSiemDestinationResponse")


@_attrs_define
class CreateSiemDestinationResponse:
    """
    Attributes:
        destination (Schema983):
        signing_secret (str): Secret used to compute the HMAC signature of delivered batches
    """

    destination: Schema983
    signing_secret: str

    def to_dict(self) -> dict[str, Any]:
        destination = self.destination.to_dict()

        signing_secret = self.signing_secret

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "destination": destination,
                "signingSecret": signing_secret,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_983 import Schema983

        d = dict(src_dict)
        destination = Schema983.from_dict(d.pop("destination"))

        signing_secret = d.pop("signingSecret")

        create_siem_destination_response = cls(
            destination=destination,
            signing_secret=signing_secret,
        )

        return create_siem_destination_response
