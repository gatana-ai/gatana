from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1052 import Schema1052
    from ..models.schema_1058 import Schema1058


T = TypeVar("T", bound="Schema1051")


@_attrs_define
class Schema1051:
    """
    Attributes:
        permission (Schema1052 | Schema1058):
        server_slug (str): Slug of the server
    """

    permission: Schema1052 | Schema1058
    server_slug: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1052 import Schema1052

        permission: dict[str, Any]
        if isinstance(self.permission, Schema1052):
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
        from ..models.schema_1052 import Schema1052
        from ..models.schema_1058 import Schema1058

        d = dict(src_dict)

        def _parse_permission(data: object) -> Schema1052 | Schema1058:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_server_member_type_0 = Schema1052.from_dict(data)

                return componentsschemas_server_member_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_server_member_type_1 = Schema1058.from_dict(data)

            return componentsschemas_server_member_type_1

        permission = _parse_permission(d.pop("permission"))

        server_slug = d.pop("serverSlug")

        schema_1051 = cls(
            permission=permission,
            server_slug=server_slug,
        )

        return schema_1051
