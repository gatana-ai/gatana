from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.schema_1456 import Schema1456
    from ..models.schema_1458 import Schema1458


T = TypeVar("T", bound="GetMcpServerSkillFileResponse")


@_attrs_define
class GetMcpServerSkillFileResponse:
    """
    Attributes:
        file (None | Schema1456): The file, verified against the skill entry of the server. null when credentials are
            missing
        credential_prompt (None | Schema1458): Set when the server needs credentials before the caller can read the file
    """

    file: None | Schema1456
    credential_prompt: None | Schema1458

    def to_dict(self) -> dict[str, Any]:
        from ..models.schema_1456 import Schema1456
        from ..models.schema_1458 import Schema1458

        file: dict[str, Any] | None
        if isinstance(self.file, Schema1456):
            file = self.file.to_dict()
        else:
            file = self.file

        credential_prompt: dict[str, Any] | None
        if isinstance(self.credential_prompt, Schema1458):
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
        from ..models.schema_1456 import Schema1456
        from ..models.schema_1458 import Schema1458

        d = dict(src_dict)

        def _parse_file(data: object) -> None | Schema1456:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1455_type_0 = Schema1456.from_dict(data)

                return componentsschemas_schema1455_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1456, data)

        file = _parse_file(d.pop("file"))

        def _parse_credential_prompt(data: object) -> None | Schema1458:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema1457_type_0 = Schema1458.from_dict(data)

                return componentsschemas_schema1457_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1458, data)

        credential_prompt = _parse_credential_prompt(d.pop("credentialPrompt"))

        get_mcp_server_skill_file_response = cls(
            file=file,
            credential_prompt=credential_prompt,
        )

        return get_mcp_server_skill_file_response
