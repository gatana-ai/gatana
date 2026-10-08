from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_101 import Schema101
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_105 import Schema105
    from ..models.schema_107 import Schema107
    from ..models.schema_108 import Schema108
    from ..models.schema_109 import Schema109


T = TypeVar("T", bound="HostedTransportConfig")


@_attrs_define
class HostedTransportConfig:
    """
    Attributes:
        type_ (Literal['hosted']): Transport type discriminator, always "hosted"
        runtime (Schema101): Runtime that executes the hosted tool functions
        env (list[list[str]] | Unset):
        limits (None | Schema105 | Unset): Deprecated: former resource ceiling, no longer applied to deployments. Use
            requests to reserve capacity instead
        requests (None | Schema107 | Unset): Resources reserved for the hosted runtime: the minimum it is guaranteed
            when the hardware is busy. Overrides the organization default
        storage (None | Schema108 | Unset): Persistent storage for the server. When enabled the server keeps one volume,
            mounted at the path in GATANA_DATA_DIR, which survives restarts and the idle stop. The size is fixed by the
            deployment and counts against the organization storage quota
        tailscale (None | Schema109 | Unset): Egress-only Tailscale access. When enabled the server can open connections
            to hosts on your tailnet, and to the subnets its routers advertise. Nothing on the tailnet can reach the server
    """

    type_: Literal["hosted"]
    runtime: Schema101
    env: list[list[str]] | Unset = UNSET
    limits: None | Schema105 | Unset = UNSET
    requests: None | Schema107 | Unset = UNSET
    storage: None | Schema108 | Unset = UNSET
    tailscale: None | Schema109 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_105 import Schema105
        from ..models.schema_107 import Schema107
        from ..models.schema_108 import Schema108
        from ..models.schema_109 import Schema109

        type_ = self.type_

        runtime = self.runtime.value

        env: list[list[str]] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = []
            for componentsschemas_schema102_item_data in self.env:
                componentsschemas_schema102_item = []
                for componentsschemas_schema102_item_item_data in componentsschemas_schema102_item_data:
                    componentsschemas_schema102_item_item: str
                    componentsschemas_schema102_item_item = componentsschemas_schema102_item_item_data
                    componentsschemas_schema102_item.append(componentsschemas_schema102_item_item)

                env.append(componentsschemas_schema102_item)

        limits: dict[str, Any] | None | Unset
        if isinstance(self.limits, Unset):
            limits = UNSET
        elif isinstance(self.limits, Schema105):
            limits = self.limits.to_dict()
        else:
            limits = self.limits

        requests: dict[str, Any] | None | Unset
        if isinstance(self.requests, Unset):
            requests = UNSET
        elif isinstance(self.requests, Schema107):
            requests = self.requests.to_dict()
        else:
            requests = self.requests

        storage: dict[str, Any] | None | Unset
        if isinstance(self.storage, Unset):
            storage = UNSET
        elif isinstance(self.storage, Schema108):
            storage = self.storage.to_dict()
        else:
            storage = self.storage

        tailscale: dict[str, Any] | None | Unset
        if isinstance(self.tailscale, Unset):
            tailscale = UNSET
        elif isinstance(self.tailscale, Schema109):
            tailscale = self.tailscale.to_dict()
        else:
            tailscale = self.tailscale

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "runtime": runtime,
            }
        )
        if env is not UNSET:
            field_dict["env"] = env
        if limits is not UNSET:
            field_dict["limits"] = limits
        if requests is not UNSET:
            field_dict["requests"] = requests
        if storage is not UNSET:
            field_dict["storage"] = storage
        if tailscale is not UNSET:
            field_dict["tailscale"] = tailscale

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_105 import Schema105
        from ..models.schema_107 import Schema107
        from ..models.schema_108 import Schema108
        from ..models.schema_109 import Schema109

        d = dict(src_dict)
        type_ = cast(Literal["hosted"], d.pop("type"))
        if type_ != "hosted":
            raise ValueError(f"type must match const 'hosted', got '{type_}'")

        runtime = Schema101(d.pop("runtime"))

        _env = d.pop("env", UNSET)
        env: list[list[str]] | Unset = UNSET
        if _env is not UNSET:
            env = []
            for componentsschemas_schema102_item_data in _env:
                componentsschemas_schema102_item = []
                _componentsschemas_schema102_item = componentsschemas_schema102_item_data
                for componentsschemas_schema102_item_item_data in _componentsschemas_schema102_item:

                    def _parse_componentsschemas_schema102_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema102_item_item = _parse_componentsschemas_schema102_item_item(
                        componentsschemas_schema102_item_item_data
                    )

                    componentsschemas_schema102_item.append(componentsschemas_schema102_item_item)

                env.append(componentsschemas_schema102_item)

        def _parse_limits(data: object) -> None | Schema105 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema104_type_0 = Schema105.from_dict(data)

                return componentsschemas_schema104_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema105 | Unset, data)

        limits = _parse_limits(d.pop("limits", UNSET))

        def _parse_requests(data: object) -> None | Schema107 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema106_type_0 = Schema107.from_dict(data)

                return componentsschemas_schema106_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema107 | Unset, data)

        requests = _parse_requests(d.pop("requests", UNSET))

        def _parse_storage(data: object) -> None | Schema108 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_hosted_transport_storage_type_0 = Schema108.from_dict(data)

                return componentsschemas_hosted_transport_storage_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema108 | Unset, data)

        storage = _parse_storage(d.pop("storage", UNSET))

        def _parse_tailscale(data: object) -> None | Schema109 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_hosted_transport_tailscale_type_0 = Schema109.from_dict(data)

                return componentsschemas_hosted_transport_tailscale_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema109 | Unset, data)

        tailscale = _parse_tailscale(d.pop("tailscale", UNSET))

        hosted_transport_config = cls(
            type_=type_,
            runtime=runtime,
            env=env,
            limits=limits,
            requests=requests,
            storage=storage,
            tailscale=tailscale,
        )

        hosted_transport_config.additional_properties = d
        return hosted_transport_config

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
