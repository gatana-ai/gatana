from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_799 import Schema799
    from ..models.schema_804 import Schema804
    from ..models.schema_805 import Schema805
    from ..models.schema_811 import Schema811


T = TypeVar("T", bound="DeploymentMetricsResponse")


@_attrs_define
class DeploymentMetricsResponse:
    """
    Attributes:
        cpu (Schema799):
        memory (Schema804):
        resource_limits (Schema805):
        storage (None | Schema811): Usage of the server's persistent volume, or null when it keeps no state or reports
            no usage
    """

    cpu: Schema799
    memory: Schema804
    resource_limits: Schema805
    storage: None | Schema811

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_811 import Schema811

        cpu = self.cpu.to_dict()

        memory = self.memory.to_dict()

        resource_limits = self.resource_limits.to_dict()

        storage: dict[str, Any] | None
        if isinstance(self.storage, Schema811):
            storage = self.storage.to_dict()
        else:
            storage = self.storage

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "cpu": cpu,
                "memory": memory,
                "resourceLimits": resource_limits,
                "storage": storage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_799 import Schema799
        from ..models.schema_804 import Schema804
        from ..models.schema_805 import Schema805
        from ..models.schema_811 import Schema811

        d = dict(src_dict)
        cpu = Schema799.from_dict(d.pop("cpu"))

        memory = Schema804.from_dict(d.pop("memory"))

        resource_limits = Schema805.from_dict(d.pop("resourceLimits"))

        def _parse_storage(data: object) -> None | Schema811:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema810_type_0 = Schema811.from_dict(data)

                return componentsschemas_schema810_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema811, data)

        storage = _parse_storage(d.pop("storage"))

        deployment_metrics_response = cls(
            cpu=cpu,
            memory=memory,
            resource_limits=resource_limits,
            storage=storage,
        )

        return deployment_metrics_response
