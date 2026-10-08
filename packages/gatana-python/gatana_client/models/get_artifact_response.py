from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_1090 import Schema1090
from ..models.schema_1091 import Schema1091
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artifact_version_meta_dto import ArtifactVersionMetaDto


T = TypeVar("T", bound="GetArtifactResponse")


@_attrs_define
class GetArtifactResponse:
    """
    Attributes:
        id (str):
        title (str):
        created_by_user_id (str):
        created_by_user_name (str): Display name of the creator, empty when no name is set
        created_by_user_email (str): Email of the creator
        visibility (Schema1090):
        theme (Schema1091):
        current_version (float):
        shared_with_user_ids (list[str]): IDs of the users the artifact is shared with
        shared_with_team_ids (list[str]): IDs of the teams the artifact is shared with
        created_at (str):
        updated_at (str):
        url (str): The viewer URL of the artifact on the tenant domain
        created_by_name (str): Display name of the creator, or their email when no name is set
        versions (list[ArtifactVersionMetaDto]):
        frame_url (str | Unset):
    """

    id: str
    title: str
    created_by_user_id: str
    created_by_user_name: str
    created_by_user_email: str
    visibility: Schema1090
    theme: Schema1091
    current_version: float
    shared_with_user_ids: list[str]
    shared_with_team_ids: list[str]
    created_at: str
    updated_at: str
    url: str
    created_by_name: str
    versions: list[ArtifactVersionMetaDto]
    frame_url: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        created_by_user_id = self.created_by_user_id

        created_by_user_name = self.created_by_user_name

        created_by_user_email = self.created_by_user_email

        visibility = self.visibility.value

        theme = self.theme.value

        current_version = self.current_version

        shared_with_user_ids = self.shared_with_user_ids

        shared_with_team_ids = self.shared_with_team_ids

        created_at = self.created_at

        updated_at = self.updated_at

        url = self.url

        created_by_name = self.created_by_name

        versions = []
        for componentsschemas_schema1102_item_data in self.versions:
            componentsschemas_schema1102_item = componentsschemas_schema1102_item_data.to_dict()
            versions.append(componentsschemas_schema1102_item)

        frame_url = self.frame_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "title": title,
                "createdByUserId": created_by_user_id,
                "createdByUserName": created_by_user_name,
                "createdByUserEmail": created_by_user_email,
                "visibility": visibility,
                "theme": theme,
                "currentVersion": current_version,
                "sharedWithUserIds": shared_with_user_ids,
                "sharedWithTeamIds": shared_with_team_ids,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "url": url,
                "createdByName": created_by_name,
                "versions": versions,
            }
        )
        if frame_url is not UNSET:
            field_dict["frameUrl"] = frame_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.artifact_version_meta_dto import ArtifactVersionMetaDto

        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        created_by_user_id = d.pop("createdByUserId")

        created_by_user_name = d.pop("createdByUserName")

        created_by_user_email = d.pop("createdByUserEmail")

        visibility = Schema1090(d.pop("visibility"))

        theme = Schema1091(d.pop("theme"))

        current_version = d.pop("currentVersion")

        shared_with_user_ids = cast(list[str], d.pop("sharedWithUserIds"))

        shared_with_team_ids = cast(list[str], d.pop("sharedWithTeamIds"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        url = d.pop("url")

        created_by_name = d.pop("createdByName")

        versions = []
        _versions = d.pop("versions")
        for componentsschemas_schema1102_item_data in _versions:
            componentsschemas_schema1102_item = ArtifactVersionMetaDto.from_dict(componentsschemas_schema1102_item_data)

            versions.append(componentsschemas_schema1102_item)

        frame_url = d.pop("frameUrl", UNSET)

        get_artifact_response = cls(
            id=id,
            title=title,
            created_by_user_id=created_by_user_id,
            created_by_user_name=created_by_user_name,
            created_by_user_email=created_by_user_email,
            visibility=visibility,
            theme=theme,
            current_version=current_version,
            shared_with_user_ids=shared_with_user_ids,
            shared_with_team_ids=shared_with_team_ids,
            created_at=created_at,
            updated_at=updated_at,
            url=url,
            created_by_name=created_by_name,
            versions=versions,
            frame_url=frame_url,
        )

        return get_artifact_response
