from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.features import Features
    from ..models.schema_463 import Schema463
    from ..models.schema_481 import Schema481
    from ..models.schema_483 import Schema483
    from ..models.schema_505 import Schema505


T = TypeVar("T", bound="AuthMetadata")


@_attrs_define
class AuthMetadata:
    """
    Attributes:
        is_playground (bool):
        has_paid_subscription (bool):
        has_assistant (bool):
        has_glama_registry (bool):
        has_sign_in_method (bool): Whether the user has a password or an SSO identity
        capabilities (Schema463):
        features (Features):
        user (Schema481):
        tenant (Schema483):
        rules (list[Any]):
        quota (Schema505):
    """

    is_playground: bool
    has_paid_subscription: bool
    has_assistant: bool
    has_glama_registry: bool
    has_sign_in_method: bool
    capabilities: Schema463
    features: Features
    user: Schema481
    tenant: Schema483
    rules: list[Any]
    quota: Schema505

    def to_dict(self) -> dict[str, Any]:
        is_playground = self.is_playground

        has_paid_subscription = self.has_paid_subscription

        has_assistant = self.has_assistant

        has_glama_registry = self.has_glama_registry

        has_sign_in_method = self.has_sign_in_method

        capabilities = self.capabilities.to_dict()

        features = self.features.to_dict()

        user = self.user.to_dict()

        tenant = self.tenant.to_dict()

        rules = self.rules

        quota = self.quota.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "isPlayground": is_playground,
                "hasPaidSubscription": has_paid_subscription,
                "hasAssistant": has_assistant,
                "hasGlamaRegistry": has_glama_registry,
                "hasSignInMethod": has_sign_in_method,
                "capabilities": capabilities,
                "features": features,
                "user": user,
                "tenant": tenant,
                "rules": rules,
                "quota": quota,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.features import Features
        from ..models.schema_463 import Schema463
        from ..models.schema_481 import Schema481
        from ..models.schema_483 import Schema483
        from ..models.schema_505 import Schema505

        d = dict(src_dict)
        is_playground = d.pop("isPlayground")

        has_paid_subscription = d.pop("hasPaidSubscription")

        has_assistant = d.pop("hasAssistant")

        has_glama_registry = d.pop("hasGlamaRegistry")

        has_sign_in_method = d.pop("hasSignInMethod")

        capabilities = Schema463.from_dict(d.pop("capabilities"))

        features = Features.from_dict(d.pop("features"))

        user = Schema481.from_dict(d.pop("user"))

        tenant = Schema483.from_dict(d.pop("tenant"))

        rules = cast(list[Any], d.pop("rules"))

        quota = Schema505.from_dict(d.pop("quota"))

        auth_metadata = cls(
            is_playground=is_playground,
            has_paid_subscription=has_paid_subscription,
            has_assistant=has_assistant,
            has_glama_registry=has_glama_registry,
            has_sign_in_method=has_sign_in_method,
            capabilities=capabilities,
            features=features,
            user=user,
            tenant=tenant,
            rules=rules,
            quota=quota,
        )

        return auth_metadata
