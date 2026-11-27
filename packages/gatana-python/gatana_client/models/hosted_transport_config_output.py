from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_647 import Schema647
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_651 import Schema651
    from ..models.schema_653 import Schema653
    from ..models.schema_654 import Schema654
    from ..models.schema_655 import Schema655


T = TypeVar("T", bound="HostedTransportConfigOutput")


@_attrs_define
class HostedTransportConfigOutput:
    """
    Attributes:
        type_ (Literal['hosted']): Transport type discriminator, always "hosted"
        runtime (Schema647): Runtime that executes the hosted tool functions
        env (list[list[str]] | Unset):
        limits (None | Schema651 | Unset): Deprecated: former resource ceiling, no longer applied to deployments. Use
            requests to reserve capacity instead
        requests (None | Schema653 | Unset): Resources reserved for the hosted runtime: the minimum it is guaranteed
            when the hardware is busy. Overrides the organization default
        storage (None | Schema654 | Unset): Persistent storage for the server. When enabled the server keeps one volume,
            mounted at the path in GATANA_DATA_DIR, which survives restarts and the idle stop. The size is fixed by the
            deployment and counts against the organization storage quota
        tailscale (None | Schema655 | Unset): Egress-only Tailscale access. When enabled the server can open connections
            to hosts on your tailnet, and to the subnets its routers advertise. Nothing on the tailnet can reach the server
    """

    type_: Literal["hosted"]
    runtime: Schema647
    env: list[list[str]] | Unset = UNSET
    limits: None | Schema651 | Unset = UNSET
    requests: None | Schema653 | Unset = UNSET
    storage: None | Schema654 | Unset = UNSET
    tailscale: None | Schema655 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_651 import Schema651
        from ..models.schema_653 import Schema653
        from ..models.schema_654 import Schema654
        from ..models.schema_655 import Schema655

        type_ = self.type_

        runtime = self.runtime.value

        env: list[list[str]] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = []
            for componentsschemas_schema648_item_data in self.env:
                componentsschemas_schema648_item = []
                for componentsschemas_schema648_item_item_data in componentsschemas_schema648_item_data:
                    componentsschemas_schema648_item_item: str
                    componentsschemas_schema648_item_item = componentsschemas_schema648_item_item_data
                    componentsschemas_schema648_item.append(componentsschemas_schema648_item_item)

                env.append(componentsschemas_schema648_item)

        limits: dict[str, Any] | None | Unset
        if isinstance(self.limits, Unset):
            limits = UNSET
        elif isinstance(self.limits, Schema651):
            limits = self.limits.to_dict()
        else:
            limits = self.limits

        requests: dict[str, Any] | None | Unset
        if isinstance(self.requests, Unset):
            requests = UNSET
        elif isinstance(self.requests, Schema653):
            requests = self.requests.to_dict()
        else:
            requests = self.requests

        storage: dict[str, Any] | None | Unset
        if isinstance(self.storage, Unset):
            storage = UNSET
        elif isinstance(self.storage, Schema654):
            storage = self.storage.to_dict()
        else:
            storage = self.storage

        tailscale: dict[str, Any] | None | Unset
        if isinstance(self.tailscale, Unset):
            tailscale = UNSET
        elif isinstance(self.tailscale, Schema655):
            tailscale = self.tailscale.to_dict()
        else:
            tailscale = self.tailscale

        field_dict: dict[str, Any] = {}

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
        from ..models.schema_651 import Schema651
        from ..models.schema_653 import Schema653
        from ..models.schema_654 import Schema654
        from ..models.schema_655 import Schema655

        d = dict(src_dict)
        type_ = cast(Literal["hosted"], d.pop("type"))
        if type_ != "hosted":
            raise ValueError(f"type must match const 'hosted', got '{type_}'")

        runtime = Schema647(d.pop("runtime"))

        _env = d.pop("env", UNSET)
        env: list[list[str]] | Unset = UNSET
        if _env is not UNSET:
            env = []
            for componentsschemas_schema648_item_data in _env:
                componentsschemas_schema648_item = []
                _componentsschemas_schema648_item = componentsschemas_schema648_item_data
                for componentsschemas_schema648_item_item_data in _componentsschemas_schema648_item:

                    def _parse_componentsschemas_schema648_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema648_item_item = _parse_componentsschemas_schema648_item_item(
                        componentsschemas_schema648_item_item_data
                    )

                    componentsschemas_schema648_item.append(componentsschemas_schema648_item_item)

                env.append(componentsschemas_schema648_item)

        def _parse_limits(data: object) -> None | Schema651 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema650_type_0 = Schema651.from_dict(data)

                return componentsschemas_schema650_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema651 | Unset, data)

        limits = _parse_limits(d.pop("limits", UNSET))

        def _parse_requests(data: object) -> None | Schema653 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema652_type_0 = Schema653.from_dict(data)

                return componentsschemas_schema652_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema653 | Unset, data)

        requests = _parse_requests(d.pop("requests", UNSET))

        def _parse_storage(data: object) -> None | Schema654 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_hosted_transport_storage_output_type_0 = Schema654.from_dict(data)

                return componentsschemas_hosted_transport_storage_output_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema654 | Unset, data)

        storage = _parse_storage(d.pop("storage", UNSET))

        def _parse_tailscale(data: object) -> None | Schema655 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_hosted_transport_tailscale_output_type_0 = Schema655.from_dict(data)

                return componentsschemas_hosted_transport_tailscale_output_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema655 | Unset, data)

        tailscale = _parse_tailscale(d.pop("tailscale", UNSET))

        hosted_transport_config_output = cls(
            type_=type_,
            runtime=runtime,
            env=env,
            limits=limits,
            requests=requests,
            storage=storage,
            tailscale=tailscale,
        )

        return hosted_transport_config_output
