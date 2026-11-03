from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_448 import Schema448
    from ..models.schema_451 import Schema451
    from ..models.schema_452 import Schema452
    from ..models.schema_453 import Schema453
    from ..models.schema_454 import Schema454
    from ..models.schema_455 import Schema455
    from ..models.schema_456 import Schema456


T = TypeVar("T", bound="Features")


@_attrs_define
class Features:
    """
    Attributes:
        stdio (Schema448):
        hosted (Schema451):
        code_mode (Schema452):
        sandbox (Schema453):
        storage (Schema454):
        tailscale (Schema455):
        server_files (Schema456):
    """

    stdio: Schema448
    hosted: Schema451
    code_mode: Schema452
    sandbox: Schema453
    storage: Schema454
    tailscale: Schema455
    server_files: Schema456

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
        from ..models.schema_448 import Schema448
        from ..models.schema_451 import Schema451
        from ..models.schema_452 import Schema452
        from ..models.schema_453 import Schema453
        from ..models.schema_454 import Schema454
        from ..models.schema_455 import Schema455
        from ..models.schema_456 import Schema456

        d = dict(src_dict)
        stdio = Schema448.from_dict(d.pop("stdio"))

        hosted = Schema451.from_dict(d.pop("hosted"))

        code_mode = Schema452.from_dict(d.pop("codeMode"))

        sandbox = Schema453.from_dict(d.pop("sandbox"))

        storage = Schema454.from_dict(d.pop("storage"))

        tailscale = Schema455.from_dict(d.pop("tailscale"))

        server_files = Schema456.from_dict(d.pop("serverFiles"))

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
