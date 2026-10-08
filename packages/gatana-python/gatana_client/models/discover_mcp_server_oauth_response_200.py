from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.server_o_auth_metadata import ServerOAuthMetadata


T = TypeVar("T", bound="DiscoverMcpServerOauthResponse200")


@_attrs_define
class DiscoverMcpServerOauthResponse200:
    """
    Attributes:
        oauth_metadata (None | ServerOAuthMetadata):
    """

    oauth_metadata: None | ServerOAuthMetadata

    def to_dict(self) -> dict[str, Any]:
        from ..models.server_o_auth_metadata import ServerOAuthMetadata

        oauth_metadata: dict[str, Any] | None
        if isinstance(self.oauth_metadata, ServerOAuthMetadata):
            oauth_metadata = self.oauth_metadata.to_dict()
        else:
            oauth_metadata = self.oauth_metadata

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "oauthMetadata": oauth_metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_o_auth_metadata import ServerOAuthMetadata

        d = dict(src_dict)

        def _parse_oauth_metadata(data: object) -> None | ServerOAuthMetadata:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                oauth_metadata_type_0 = ServerOAuthMetadata.from_dict(data)

                return oauth_metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServerOAuthMetadata, data)

        oauth_metadata = _parse_oauth_metadata(d.pop("oauthMetadata"))

        discover_mcp_server_oauth_response_200 = cls(
            oauth_metadata=oauth_metadata,
        )

        return discover_mcp_server_oauth_response_200
