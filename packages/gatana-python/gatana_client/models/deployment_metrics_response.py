from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_858 import Schema858
    from ..models.schema_863 import Schema863
    from ..models.schema_864 import Schema864
    from ..models.schema_870 import Schema870


T = TypeVar("T", bound="DeploymentMetricsResponse")


@_attrs_define
class DeploymentMetricsResponse:
    """
    Attributes:
        cpu (Schema858):
        memory (Schema863):
        resource_limits (Schema864):
        storage (None | Schema870): Usage of the server's persistent volume, or null when it keeps no state or reports
            no usage
    """

    cpu: Schema858
    memory: Schema863
    resource_limits: Schema864
    storage: None | Schema870

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_870 import Schema870

        cpu = self.cpu.to_dict()

        memory = self.memory.to_dict()

        resource_limits = self.resource_limits.to_dict()

        storage: dict[str, Any] | None
        if isinstance(self.storage, Schema870):
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
        from ..models.schema_858 import Schema858
        from ..models.schema_863 import Schema863
        from ..models.schema_864 import Schema864
        from ..models.schema_870 import Schema870

        d = dict(src_dict)
        cpu = Schema858.from_dict(d.pop("cpu"))

        memory = Schema863.from_dict(d.pop("memory"))

        resource_limits = Schema864.from_dict(d.pop("resourceLimits"))

        def _parse_storage(data: object) -> None | Schema870:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema869_type_0 = Schema870.from_dict(data)

                return componentsschemas_schema869_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema870, data)

        storage = _parse_storage(d.pop("storage"))

        deployment_metrics_response = cls(
            cpu=cpu,
            memory=memory,
            resource_limits=resource_limits,
            storage=storage,
        )

        return deployment_metrics_response
