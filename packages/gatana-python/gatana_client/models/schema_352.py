from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_353 import Schema353
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_354 import Schema354
    from ..models.server_resource_requests import ServerResourceRequests
    from ..models.tenant_abilities import TenantAbilities


T = TypeVar("T", bound="Schema352")


@_attrs_define
class Schema352:
    """
    Attributes:
        id (str):
        is_mcp_authorization_api_key_enabled (bool):
        is_output_compression_allowed (bool):
        grant_users_install_servers_policy (bool):
        display_name (str):
        is_trial (bool):
        is_per_seat_subscription (bool):
        subscription_plan (str):
        subscription_seats (float):
        member_default_role (Literal['none'] | Schema353):
        free_credits (float):
        paid_credits (float):
        default_resource_limits (Schema354):
        default_resource_requests (ServerResourceRequests):
        abilities (TenantAbilities):
        trial_end_date (None | str):
        trial_extended_for_feedback (bool):
        number_of_enabled_users (float | Unset):
    """

    id: str
    is_mcp_authorization_api_key_enabled: bool
    is_output_compression_allowed: bool
    grant_users_install_servers_policy: bool
    display_name: str
    is_trial: bool
    is_per_seat_subscription: bool
    subscription_plan: str
    subscription_seats: float
    member_default_role: Literal["none"] | Schema353
    free_credits: float
    paid_credits: float
    default_resource_limits: Schema354
    default_resource_requests: ServerResourceRequests
    abilities: TenantAbilities
    trial_end_date: None | str
    trial_extended_for_feedback: bool
    number_of_enabled_users: float | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        is_mcp_authorization_api_key_enabled = self.is_mcp_authorization_api_key_enabled

        is_output_compression_allowed = self.is_output_compression_allowed

        grant_users_install_servers_policy = self.grant_users_install_servers_policy

        display_name = self.display_name

        is_trial = self.is_trial

        is_per_seat_subscription = self.is_per_seat_subscription

        subscription_plan = self.subscription_plan

        subscription_seats = self.subscription_seats

        member_default_role: Literal["none"] | str
        if isinstance(self.member_default_role, Schema353):
            member_default_role = self.member_default_role.value
        else:
            member_default_role = self.member_default_role

        free_credits = self.free_credits

        paid_credits = self.paid_credits

        default_resource_limits = self.default_resource_limits.to_dict()

        default_resource_requests = self.default_resource_requests.to_dict()

        abilities = self.abilities.to_dict()

        trial_end_date: None | str
        trial_end_date = self.trial_end_date

        trial_extended_for_feedback = self.trial_extended_for_feedback

        number_of_enabled_users = self.number_of_enabled_users

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "isMcpAuthorizationApiKeyEnabled": is_mcp_authorization_api_key_enabled,
                "isOutputCompressionAllowed": is_output_compression_allowed,
                "grantUsersInstallServersPolicy": grant_users_install_servers_policy,
                "displayName": display_name,
                "isTrial": is_trial,
                "isPerSeatSubscription": is_per_seat_subscription,
                "subscriptionPlan": subscription_plan,
                "subscriptionSeats": subscription_seats,
                "memberDefaultRole": member_default_role,
                "freeCredits": free_credits,
                "paidCredits": paid_credits,
                "defaultResourceLimits": default_resource_limits,
                "defaultResourceRequests": default_resource_requests,
                "abilities": abilities,
                "trialEndDate": trial_end_date,
                "trialExtendedForFeedback": trial_extended_for_feedback,
            }
        )
        if number_of_enabled_users is not UNSET:
            field_dict["numberOfEnabledUsers"] = number_of_enabled_users

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_354 import Schema354
        from ..models.server_resource_requests import ServerResourceRequests
        from ..models.tenant_abilities import TenantAbilities

        d = dict(src_dict)
        id = d.pop("id")

        is_mcp_authorization_api_key_enabled = d.pop("isMcpAuthorizationApiKeyEnabled")

        is_output_compression_allowed = d.pop("isOutputCompressionAllowed")

        grant_users_install_servers_policy = d.pop("grantUsersInstallServersPolicy")

        display_name = d.pop("displayName")

        is_trial = d.pop("isTrial")

        is_per_seat_subscription = d.pop("isPerSeatSubscription")

        subscription_plan = d.pop("subscriptionPlan")

        subscription_seats = d.pop("subscriptionSeats")

        def _parse_member_default_role(data: object) -> Literal["none"] | Schema353:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                member_default_role_type_0 = Schema353(data)

                return member_default_role_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            member_default_role_type_1 = cast(Literal["none"], data)
            if member_default_role_type_1 != "none":
                raise ValueError(
                    f"memberDefaultRole_type_1 must match const 'none', got '{member_default_role_type_1}'"
                )
            return member_default_role_type_1

        member_default_role = _parse_member_default_role(d.pop("memberDefaultRole"))

        free_credits = d.pop("freeCredits")

        paid_credits = d.pop("paidCredits")

        default_resource_limits = Schema354.from_dict(d.pop("defaultResourceLimits"))

        default_resource_requests = ServerResourceRequests.from_dict(d.pop("defaultResourceRequests"))

        abilities = TenantAbilities.from_dict(d.pop("abilities"))

        def _parse_trial_end_date(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        trial_end_date = _parse_trial_end_date(d.pop("trialEndDate"))

        trial_extended_for_feedback = d.pop("trialExtendedForFeedback")

        number_of_enabled_users = d.pop("numberOfEnabledUsers", UNSET)

        schema_352 = cls(
            id=id,
            is_mcp_authorization_api_key_enabled=is_mcp_authorization_api_key_enabled,
            is_output_compression_allowed=is_output_compression_allowed,
            grant_users_install_servers_policy=grant_users_install_servers_policy,
            display_name=display_name,
            is_trial=is_trial,
            is_per_seat_subscription=is_per_seat_subscription,
            subscription_plan=subscription_plan,
            subscription_seats=subscription_seats,
            member_default_role=member_default_role,
            free_credits=free_credits,
            paid_credits=paid_credits,
            default_resource_limits=default_resource_limits,
            default_resource_requests=default_resource_requests,
            abilities=abilities,
            trial_end_date=trial_end_date,
            trial_extended_for_feedback=trial_extended_for_feedback,
            number_of_enabled_users=number_of_enabled_users,
        )

        return schema_352
