from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.list_deployments_logs_response_200_logs import ListDeploymentsLogsResponse200Logs


T = TypeVar("T", bound="ListDeploymentsLogsResponse200")


@_attrs_define
class ListDeploymentsLogsResponse200:
    """
    Attributes:
        logs (ListDeploymentsLogsResponse200Logs): Container logs
    """

    logs: ListDeploymentsLogsResponse200Logs

    def to_dict(self) -> dict[str, Any]:
        logs = self.logs.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "logs": logs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_deployments_logs_response_200_logs import ListDeploymentsLogsResponse200Logs

        d = dict(src_dict)
        logs = ListDeploymentsLogsResponse200Logs.from_dict(d.pop("logs"))

        list_deployments_logs_response_200 = cls(
            logs=logs,
        )

        return list_deployments_logs_response_200
