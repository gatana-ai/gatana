from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1496 import Schema1496
    from ..models.schema_1499 import Schema1499


T = TypeVar("T", bound="GetMcpServerAppPageResponse")


@_attrs_define
class GetMcpServerAppPageResponse:
    """
    Attributes:
        page (None | Schema1496): App page. Null if credentials are missing
        credential_prompt (None | Schema1499): Prompt for missing server credentials
    """

    page: None | Schema1496
    credential_prompt: None | Schema1499

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1496 import Schema1496
        from ..models.schema_1499 import Schema1499

        page: dict[str, Any] | None
        if isinstance(self.page, Schema1496):
            page = self.page.to_dict()
        else:
            page = self.page

        credential_prompt: dict[str, Any] | None
        if isinstance(self.credential_prompt, Schema1499):
            credential_prompt = self.credential_prompt.to_dict()
        else:
            credential_prompt = self.credential_prompt

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "page": page,
                "credentialPrompt": credential_prompt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1496 import Schema1496
        from ..models.schema_1499 import Schema1499

        d = dict(src_dict)

        def _parse_page(data: object) -> None | Schema1496:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1495_type_0 = Schema1496.from_dict(data)

                return componentsschemas_schema1495_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1496, data)

        page = _parse_page(d.pop("page"))

        def _parse_credential_prompt(data: object) -> None | Schema1499:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1498_type_0 = Schema1499.from_dict(data)

                return componentsschemas_schema1498_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1499, data)

        credential_prompt = _parse_credential_prompt(d.pop("credentialPrompt"))

        get_mcp_server_app_page_response = cls(
            page=page,
            credential_prompt=credential_prompt,
        )

        return get_mcp_server_app_page_response
