from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1111 import Schema1111
    from ..models.schema_1117 import Schema1117


T = TypeVar("T", bound="Schema1110")


@_attrs_define
class Schema1110:
    """
    Attributes:
        permission (Schema1111 | Schema1117):
        server_slug (str): Slug of the server
    """

    permission: Schema1111 | Schema1117
    server_slug: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1111 import Schema1111

        permission: dict[str, Any]
        if isinstance(self.permission, Schema1111):
            permission = self.permission.to_dict()
        else:
            permission = self.permission.to_dict()

        server_slug = self.server_slug

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "permission": permission,
                "serverSlug": server_slug,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1111 import Schema1111
        from ..models.schema_1117 import Schema1117

        d = dict(src_dict)

        def _parse_permission(data: object) -> Schema1111 | Schema1117:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_server_member_type_0 = Schema1111.from_dict(data)

                return componentsschemas_server_member_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_server_member_type_1 = Schema1117.from_dict(data)

            return componentsschemas_server_member_type_1

        permission = _parse_permission(d.pop("permission"))

        server_slug = d.pop("serverSlug")

        schema_1110 = cls(
            permission=permission,
            server_slug=server_slug,
        )

        return schema_1110
