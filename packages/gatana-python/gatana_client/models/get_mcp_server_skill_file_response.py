from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1491 import Schema1491
    from ..models.schema_1493 import Schema1493


T = TypeVar("T", bound="GetMcpServerSkillFileResponse")


@_attrs_define
class GetMcpServerSkillFileResponse:
    """
    Attributes:
        file (None | Schema1491): The file, verified against the skill entry of the server. null when credentials are
            missing
        credential_prompt (None | Schema1493): Set when the server needs credentials before the caller can read the file
    """

    file: None | Schema1491
    credential_prompt: None | Schema1493

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1491 import Schema1491
        from ..models.schema_1493 import Schema1493

        file: dict[str, Any] | None
        if isinstance(self.file, Schema1491):
            file = self.file.to_dict()
        else:
            file = self.file

        credential_prompt: dict[str, Any] | None
        if isinstance(self.credential_prompt, Schema1493):
            credential_prompt = self.credential_prompt.to_dict()
        else:
            credential_prompt = self.credential_prompt

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "file": file,
                "credentialPrompt": credential_prompt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_1491 import Schema1491
        from ..models.schema_1493 import Schema1493

        d = dict(src_dict)

        def _parse_file(data: object) -> None | Schema1491:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1490_type_0 = Schema1491.from_dict(data)

                return componentsschemas_schema1490_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1491, data)

        file = _parse_file(d.pop("file"))

        def _parse_credential_prompt(data: object) -> None | Schema1493:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1492_type_0 = Schema1493.from_dict(data)

                return componentsschemas_schema1492_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1493, data)

        credential_prompt = _parse_credential_prompt(d.pop("credentialPrompt"))

        get_mcp_server_skill_file_response = cls(
            file=file,
            credential_prompt=credential_prompt,
        )

        return get_mcp_server_skill_file_response
