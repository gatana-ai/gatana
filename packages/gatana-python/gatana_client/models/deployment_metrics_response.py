from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1041 import Schema1041
    from ..models.schema_1046 import Schema1046
    from ..models.schema_1047 import Schema1047
    from ..models.schema_1053 import Schema1053


T = TypeVar("T", bound="DeploymentMetricsResponse")


@_attrs_define
class DeploymentMetricsResponse:
    """
    Attributes:
        cpu (Schema1041):
        memory (Schema1046):
        resource_limits (Schema1047):
        storage (None | Schema1053): Usage of the server's persistent volume, or null when it keeps no state or reports
            no usage
    """

    cpu: Schema1041
    memory: Schema1046
    resource_limits: Schema1047
    storage: None | Schema1053

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1053 import Schema1053

        cpu = self.cpu.to_dict()

        memory = self.memory.to_dict()

        resource_limits = self.resource_limits.to_dict()

        storage: dict[str, Any] | None
        if isinstance(self.storage, Schema1053):
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
        from ..models.schema_1041 import Schema1041
        from ..models.schema_1046 import Schema1046
        from ..models.schema_1047 import Schema1047
        from ..models.schema_1053 import Schema1053

        d = dict(src_dict)
        cpu = Schema1041.from_dict(d.pop("cpu"))

        memory = Schema1046.from_dict(d.pop("memory"))

        resource_limits = Schema1047.from_dict(d.pop("resourceLimits"))

        def _parse_storage(data: object) -> None | Schema1053:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1052_type_0 = Schema1053.from_dict(data)

                return componentsschemas_schema1052_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1053, data)

        storage = _parse_storage(d.pop("storage"))

        deployment_metrics_response = cls(
            cpu=cpu,
            memory=memory,
            resource_limits=resource_limits,
            storage=storage,
        )

        return deployment_metrics_response
