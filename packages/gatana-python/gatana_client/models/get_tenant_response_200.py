from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.tenant_dto import TenantDto


T = TypeVar("T", bound="GetTenantResponse200")


@_attrs_define
class GetTenantResponse200:
    """
    Attributes:
        tenant (TenantDto):
    """

    tenant: TenantDto

    def to_dict(self) -> dict[str, Any]:
        tenant = self.tenant.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tenant": tenant,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tenant_dto import TenantDto

        d = dict(src_dict)
        tenant = TenantDto.from_dict(d.pop("tenant"))

        get_tenant_response_200 = cls(
            tenant=tenant,
        )

        return get_tenant_response_200
