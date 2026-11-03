from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_589 import Schema589
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_594 import Schema594
    from ..models.schema_601 import Schema601
    from ..models.schema_603 import Schema603
    from ..models.schema_604 import Schema604
    from ..models.schema_605 import Schema605


T = TypeVar("T", bound="StdioTransportConfigOutput")


@_attrs_define
class StdioTransportConfigOutput:
    """
    Attributes:
        type_ (Literal['stdio']): Transport type discriminator, always "stdio"
        command (str): Command line that starts the MCP server process
        transport (Schema589): Protocol that the launched process speaks
        docker_image (str | Unset):
        env (list[list[str]] | Unset):
        http_port (float | None | Unset): Port that the process listens on when transport is HTTP-based
        url_path (None | str | Unset): URL path of the MCP endpoint when transport is HTTP-based
        health_check (Schema594 | Unset):
        limits (None | Schema601 | Unset): Deprecated: former resource ceiling, no longer applied to deployments. Use
            requests to reserve capacity instead
        requests (None | Schema603 | Unset): Resources reserved for the process: the minimum it is guaranteed when the
            hardware is busy. Overrides the organization default
        storage (None | Schema604 | Unset): Persistent storage for the server. When enabled the server keeps one volume,
            mounted at the path in GATANA_DATA_DIR, which survives restarts and the idle stop. The size is fixed by the
            deployment and counts against the organization storage quota
        tailscale (None | Schema605 | Unset): Egress-only Tailscale access. When enabled the server can open connections
            to hosts on your tailnet, and to the subnets its routers advertise. Nothing on the tailnet can reach the server
    """

    type_: Literal["stdio"]
    command: str
    transport: Schema589
    docker_image: str | Unset = UNSET
    env: list[list[str]] | Unset = UNSET
    http_port: float | None | Unset = UNSET
    url_path: None | str | Unset = UNSET
    health_check: Schema594 | Unset = UNSET
    limits: None | Schema601 | Unset = UNSET
    requests: None | Schema603 | Unset = UNSET
    storage: None | Schema604 | Unset = UNSET
    tailscale: None | Schema605 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_601 import Schema601
        from ..models.schema_603 import Schema603
        from ..models.schema_604 import Schema604
        from ..models.schema_605 import Schema605

        type_ = self.type_

        command = self.command

        transport = self.transport.value

        docker_image = self.docker_image

        env: list[list[str]] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = []
            for componentsschemas_schema587_item_data in self.env:
                componentsschemas_schema587_item = []
                for componentsschemas_schema587_item_item_data in componentsschemas_schema587_item_data:
                    componentsschemas_schema587_item_item: str
                    componentsschemas_schema587_item_item = componentsschemas_schema587_item_item_data
                    componentsschemas_schema587_item.append(componentsschemas_schema587_item_item)

                env.append(componentsschemas_schema587_item)

        http_port: float | None | Unset
        if isinstance(self.http_port, Unset):
            http_port = UNSET
        else:
            http_port = self.http_port

        url_path: None | str | Unset
        if isinstance(self.url_path, Unset):
            url_path = UNSET
        else:
            url_path = self.url_path

        health_check: dict[str, Any] | Unset = UNSET
        if not isinstance(self.health_check, Unset):
            health_check = self.health_check.to_dict()

        limits: dict[str, Any] | None | Unset
        if isinstance(self.limits, Unset):
            limits = UNSET
        elif isinstance(self.limits, Schema601):
            limits = self.limits.to_dict()
        else:
            limits = self.limits

        requests: dict[str, Any] | None | Unset
        if isinstance(self.requests, Unset):
            requests = UNSET
        elif isinstance(self.requests, Schema603):
            requests = self.requests.to_dict()
        else:
            requests = self.requests

        storage: dict[str, Any] | None | Unset
        if isinstance(self.storage, Unset):
            storage = UNSET
        elif isinstance(self.storage, Schema604):
            storage = self.storage.to_dict()
        else:
            storage = self.storage

        tailscale: dict[str, Any] | None | Unset
        if isinstance(self.tailscale, Unset):
            tailscale = UNSET
        elif isinstance(self.tailscale, Schema605):
            tailscale = self.tailscale.to_dict()
        else:
            tailscale = self.tailscale

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "command": command,
                "transport": transport,
            }
        )
        if docker_image is not UNSET:
            field_dict["dockerImage"] = docker_image
        if env is not UNSET:
            field_dict["env"] = env
        if http_port is not UNSET:
            field_dict["httpPort"] = http_port
        if url_path is not UNSET:
            field_dict["urlPath"] = url_path
        if health_check is not UNSET:
            field_dict["healthCheck"] = health_check
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
        from ..models.schema_594 import Schema594
        from ..models.schema_601 import Schema601
        from ..models.schema_603 import Schema603
        from ..models.schema_604 import Schema604
        from ..models.schema_605 import Schema605

        d = dict(src_dict)
        type_ = cast(Literal["stdio"], d.pop("type"))
        if type_ != "stdio":
            raise ValueError(f"type must match const 'stdio', got '{type_}'")

        command = d.pop("command")

        transport = Schema589(d.pop("transport"))

        docker_image = d.pop("dockerImage", UNSET)

        _env = d.pop("env", UNSET)
        env: list[list[str]] | Unset = UNSET
        if _env is not UNSET:
            env = []
            for componentsschemas_schema587_item_data in _env:
                componentsschemas_schema587_item = []
                _componentsschemas_schema587_item = componentsschemas_schema587_item_data
                for componentsschemas_schema587_item_item_data in _componentsschemas_schema587_item:

                    def _parse_componentsschemas_schema587_item_item(data: object) -> str:
                        return cast(str, data)

                    componentsschemas_schema587_item_item = _parse_componentsschemas_schema587_item_item(
                        componentsschemas_schema587_item_item_data
                    )

                    componentsschemas_schema587_item.append(componentsschemas_schema587_item_item)

                env.append(componentsschemas_schema587_item)

        def _parse_http_port(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        http_port = _parse_http_port(d.pop("httpPort", UNSET))

        def _parse_url_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url_path = _parse_url_path(d.pop("urlPath", UNSET))

        _health_check = d.pop("healthCheck", UNSET)
        health_check: Schema594 | Unset
        if isinstance(_health_check, Unset):
            health_check = UNSET
        else:
            health_check = Schema594.from_dict(_health_check)

        def _parse_limits(data: object) -> None | Schema601 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema600_type_0 = Schema601.from_dict(data)

                return componentsschemas_schema600_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema601 | Unset, data)

        limits = _parse_limits(d.pop("limits", UNSET))

        def _parse_requests(data: object) -> None | Schema603 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema602_type_0 = Schema603.from_dict(data)

                return componentsschemas_schema602_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema603 | Unset, data)

        requests = _parse_requests(d.pop("requests", UNSET))

        def _parse_storage(data: object) -> None | Schema604 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stdio_transport_storage_output_type_0 = Schema604.from_dict(data)

                return componentsschemas_stdio_transport_storage_output_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema604 | Unset, data)

        storage = _parse_storage(d.pop("storage", UNSET))

        def _parse_tailscale(data: object) -> None | Schema605 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stdio_transport_tailscale_output_type_0 = Schema605.from_dict(data)

                return componentsschemas_stdio_transport_tailscale_output_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema605 | Unset, data)

        tailscale = _parse_tailscale(d.pop("tailscale", UNSET))

        stdio_transport_config_output = cls(
            type_=type_,
            command=command,
            transport=transport,
            docker_image=docker_image,
            env=env,
            http_port=http_port,
            url_path=url_path,
            health_check=health_check,
            limits=limits,
            requests=requests,
            storage=storage,
            tailscale=tailscale,
        )

        return stdio_transport_config_output
