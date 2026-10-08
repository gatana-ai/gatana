from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_755 import Schema755


T = TypeVar("T", bound="Schema751")


@_attrs_define
class Schema751:
    """
    Attributes:
        has_payment_method (bool): Whether a default payment method is set
        trial_ends_at (None | str): Time when the trial ends, or null if not in a trial
        status (str): Stripe subscription status
        current_period_end (str): Time when the current billing period ends
        cancels_at (None | str): Time when the subscription cancels, or null if it does not cancel
        per_seat_amount (float): Price per seat in the subscription currency
        currency (str): Currency of the subscription
        card (None | Schema755): Details of the default card, or null when no card is set
        payment_type (None | str | Unset):
    """

    has_payment_method: bool
    trial_ends_at: None | str
    status: str
    current_period_end: str
    cancels_at: None | str
    per_seat_amount: float
    currency: str
    card: None | Schema755
    payment_type: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_755 import Schema755

        has_payment_method = self.has_payment_method

        trial_ends_at: None | str
        trial_ends_at = self.trial_ends_at

        status = self.status

        current_period_end = self.current_period_end

        cancels_at: None | str
        cancels_at = self.cancels_at

        per_seat_amount = self.per_seat_amount

        currency = self.currency

        card: dict[str, Any] | None
        if isinstance(self.card, Schema755):
            card = self.card.to_dict()
        else:
            card = self.card

        payment_type: None | str | Unset
        if isinstance(self.payment_type, Unset):
            payment_type = UNSET
        else:
            payment_type = self.payment_type

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "hasPaymentMethod": has_payment_method,
                "trialEndsAt": trial_ends_at,
                "status": status,
                "currentPeriodEnd": current_period_end,
                "cancelsAt": cancels_at,
                "perSeatAmount": per_seat_amount,
                "currency": currency,
                "card": card,
            }
        )
        if payment_type is not UNSET:
            field_dict["paymentType"] = payment_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_755 import Schema755

        d = dict(src_dict)
        has_payment_method = d.pop("hasPaymentMethod")

        def _parse_trial_ends_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        trial_ends_at = _parse_trial_ends_at(d.pop("trialEndsAt"))

        status = d.pop("status")

        current_period_end = d.pop("currentPeriodEnd")

        def _parse_cancels_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        cancels_at = _parse_cancels_at(d.pop("cancelsAt"))

        per_seat_amount = d.pop("perSeatAmount")

        currency = d.pop("currency")

        def _parse_card(data: object) -> None | Schema755:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                card_type_0 = Schema755.from_dict(data)

                return card_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema755, data)

        card = _parse_card(d.pop("card"))

        def _parse_payment_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        payment_type = _parse_payment_type(d.pop("paymentType", UNSET))

        schema_751 = cls(
            has_payment_method=has_payment_method,
            trial_ends_at=trial_ends_at,
            status=status,
            current_period_end=current_period_end,
            cancels_at=cancels_at,
            per_seat_amount=per_seat_amount,
            currency=currency,
            card=card,
            payment_type=payment_type,
        )

        return schema_751
