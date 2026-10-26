from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_402 import Schema402
    from ..models.schema_404 import Schema404
    from ..models.schema_425 import Schema425


T = TypeVar("T", bound="AuthMetadata")


@_attrs_define
class AuthMetadata:
    """
    Attributes:
        is_playground (bool):
        has_paid_subscription (bool):
        has_assistant (bool):
        has_glama_registry (bool):
        user (Schema402):
        tenant (Schema404):
        rules (list[Any]):
        quota (Schema425):
    """

    is_playground: bool
    has_paid_subscription: bool
    has_assistant: bool
    has_glama_registry: bool
    user: Schema402
    tenant: Schema404
    rules: list[Any]
    quota: Schema425

    def to_dict(self) -> dict[str, Any]:
        is_playground = self.is_playground

        has_paid_subscription = self.has_paid_subscription

        has_assistant = self.has_assistant

        has_glama_registry = self.has_glama_registry

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
                "user": user,
                "tenant": tenant,
                "rules": rules,
                "quota": quota,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_402 import Schema402
        from ..models.schema_404 import Schema404
        from ..models.schema_425 import Schema425

        d = dict(src_dict)
        is_playground = d.pop("isPlayground")

        has_paid_subscription = d.pop("hasPaidSubscription")

        has_assistant = d.pop("hasAssistant")

        has_glama_registry = d.pop("hasGlamaRegistry")

        user = Schema402.from_dict(d.pop("user"))

        tenant = Schema404.from_dict(d.pop("tenant"))

        rules = cast(list[Any], d.pop("rules"))

        quota = Schema425.from_dict(d.pop("quota"))

        auth_metadata = cls(
            is_playground=is_playground,
            has_paid_subscription=has_paid_subscription,
            has_assistant=has_assistant,
            has_glama_registry=has_glama_registry,
            user=user,
            tenant=tenant,
            rules=rules,
            quota=quota,
        )

        return auth_metadata
