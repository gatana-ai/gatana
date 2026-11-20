from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.server_info_icon import ServerInfoIcon


T = TypeVar("T", bound="ServerInfo")


@_attrs_define
class ServerInfo:
    """Unverified metadata from the server. Each tool refresh saves the latest server/discover result

    Attributes:
        title (str): Display name of the server, or an empty string
        version (str): Version of the server software
        website_url (str): http: or https: URL of the website, or an empty string
        description (str): Description of the server, or an empty string
        icons (list[ServerInfoIcon]): Server icons, up to one per theme. A signed-in browser can load an image from GET
            /api/v1/mcp-servers/{slug}/icon?theme=light|dark
    """

    title: str
    version: str
    website_url: str
    description: str
    icons: list[ServerInfoIcon]

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        version = self.version

        website_url = self.website_url

        description = self.description

        icons = []
        for componentsschemas_schema781_item_data in self.icons:
            componentsschemas_schema781_item = componentsschemas_schema781_item_data.to_dict()
            icons.append(componentsschemas_schema781_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "title": title,
                "version": version,
                "websiteUrl": website_url,
                "description": description,
                "icons": icons,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_info_icon import ServerInfoIcon

        d = dict(src_dict)
        title = d.pop("title")

        version = d.pop("version")

        website_url = d.pop("websiteUrl")

        description = d.pop("description")

        icons = []
        _icons = d.pop("icons")
        for componentsschemas_schema781_item_data in _icons:
            componentsschemas_schema781_item = ServerInfoIcon.from_dict(componentsschemas_schema781_item_data)

            icons.append(componentsschemas_schema781_item)

        server_info = cls(
            title=title,
            version=version,
            website_url=website_url,
            description=description,
            icons=icons,
        )

        return server_info
