from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_751 import Schema751


T = TypeVar("T", bound="GetSubscriptionResponse")


@_attrs_define
class GetSubscriptionResponse:
    """
    Attributes:
        subscription_plan (str): Name of the subscription plan
        subscription_seats (float): Number of seats in the subscription
        subscription (None | Schema751): Details of the Stripe subscription, or null when there is none
    """

    subscription_plan: str
    subscription_seats: float
    subscription: None | Schema751

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_751 import Schema751

        subscription_plan = self.subscription_plan

        subscription_seats = self.subscription_seats

        subscription: dict[str, Any] | None
        if isinstance(self.subscription, Schema751):
            subscription = self.subscription.to_dict()
        else:
            subscription = self.subscription

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "subscriptionPlan": subscription_plan,
                "subscriptionSeats": subscription_seats,
                "subscription": subscription,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_751 import Schema751

        d = dict(src_dict)
        subscription_plan = d.pop("subscriptionPlan")

        subscription_seats = d.pop("subscriptionSeats")

        def _parse_subscription(data: object) -> None | Schema751:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema750_type_0 = Schema751.from_dict(data)

                return componentsschemas_schema750_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema751, data)

        subscription = _parse_subscription(d.pop("subscription"))

        get_subscription_response = cls(
            subscription_plan=subscription_plan,
            subscription_seats=subscription_seats,
            subscription=subscription,
        )

        return get_subscription_response
