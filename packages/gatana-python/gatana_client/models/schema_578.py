from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.server_dto import ServerDto
    from ..models.server_file import ServerFile


T = TypeVar("T", bound="Schema578")


@_attrs_define
class Schema578:
    """
    Attributes:
        server (ServerDto):
        files (list[ServerFile]):
    """

    server: ServerDto
    files: list[ServerFile]

    def to_dict(self) -> dict[str, Any]:
        server = self.server.to_dict()

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "server": server,
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_dto import ServerDto
        from ..models.server_file import ServerFile

        d = dict(src_dict)
        server = ServerDto.from_dict(d.pop("server"))

        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = ServerFile.from_dict(files_item_data)

            files.append(files_item)

        schema_578 = cls(
            server=server,
            files=files,
        )

        return schema_578
