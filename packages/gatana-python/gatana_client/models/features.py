from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_472 import Schema472
    from ..models.schema_475 import Schema475
    from ..models.schema_476 import Schema476
    from ..models.schema_477 import Schema477
    from ..models.schema_478 import Schema478
    from ..models.schema_479 import Schema479
    from ..models.schema_480 import Schema480


T = TypeVar("T", bound="Features")


@_attrs_define
class Features:
    """
    Attributes:
        stdio (Schema472):
        hosted (Schema475):
        code_mode (Schema476):
        sandbox (Schema477):
        storage (Schema478):
        tailscale (Schema479):
        server_files (Schema480):
    """

    stdio: Schema472
    hosted: Schema475
    code_mode: Schema476
    sandbox: Schema477
    storage: Schema478
    tailscale: Schema479
    server_files: Schema480

    def to_dict(self) -> dict[str, Any]:
        stdio = self.stdio.to_dict()

        hosted = self.hosted.to_dict()

        code_mode = self.code_mode.to_dict()

        sandbox = self.sandbox.to_dict()

        storage = self.storage.to_dict()

        tailscale = self.tailscale.to_dict()

        server_files = self.server_files.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "stdio": stdio,
                "hosted": hosted,
                "codeMode": code_mode,
                "sandbox": sandbox,
                "storage": storage,
                "tailscale": tailscale,
                "serverFiles": server_files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_472 import Schema472
        from ..models.schema_475 import Schema475
        from ..models.schema_476 import Schema476
        from ..models.schema_477 import Schema477
        from ..models.schema_478 import Schema478
        from ..models.schema_479 import Schema479
        from ..models.schema_480 import Schema480

        d = dict(src_dict)
        stdio = Schema472.from_dict(d.pop("stdio"))

        hosted = Schema475.from_dict(d.pop("hosted"))

        code_mode = Schema476.from_dict(d.pop("codeMode"))

        sandbox = Schema477.from_dict(d.pop("sandbox"))

        storage = Schema478.from_dict(d.pop("storage"))

        tailscale = Schema479.from_dict(d.pop("tailscale"))

        server_files = Schema480.from_dict(d.pop("serverFiles"))

        features = cls(
            stdio=stdio,
            hosted=hosted,
            code_mode=code_mode,
            sandbox=sandbox,
            storage=storage,
            tailscale=tailscale,
            server_files=server_files,
        )

        return features
