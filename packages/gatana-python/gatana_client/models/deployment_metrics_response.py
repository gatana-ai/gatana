from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1031 import Schema1031
    from ..models.schema_1036 import Schema1036
    from ..models.schema_1037 import Schema1037
    from ..models.schema_1043 import Schema1043


T = TypeVar("T", bound="DeploymentMetricsResponse")


@_attrs_define
class DeploymentMetricsResponse:
    """
    Attributes:
        cpu (Schema1031):
        memory (Schema1036):
        resource_limits (Schema1037):
        storage (None | Schema1043): Usage of the server's persistent volume, or null when it keeps no state or reports
            no usage
    """

    cpu: Schema1031
    memory: Schema1036
    resource_limits: Schema1037
    storage: None | Schema1043

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1043 import Schema1043

        cpu = self.cpu.to_dict()

        memory = self.memory.to_dict()

        resource_limits = self.resource_limits.to_dict()

        storage: dict[str, Any] | None
        if isinstance(self.storage, Schema1043):
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
        from ..models.schema_1031 import Schema1031
        from ..models.schema_1036 import Schema1036
        from ..models.schema_1037 import Schema1037
        from ..models.schema_1043 import Schema1043

        d = dict(src_dict)
        cpu = Schema1031.from_dict(d.pop("cpu"))

        memory = Schema1036.from_dict(d.pop("memory"))

        resource_limits = Schema1037.from_dict(d.pop("resourceLimits"))

        def _parse_storage(data: object) -> None | Schema1043:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1042_type_0 = Schema1043.from_dict(data)

                return componentsschemas_schema1042_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1043, data)

        storage = _parse_storage(d.pop("storage"))

        deployment_metrics_response = cls(
            cpu=cpu,
            memory=memory,
            resource_limits=resource_limits,
            storage=storage,
        )

        return deployment_metrics_response
