from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_1123 import Schema1123

T = TypeVar("T", bound="GetSkillResponse")


@_attrs_define
class GetSkillResponse:
    """
    Attributes:
        id (str):
        name (str): Unique name in the organization; how agents address the skill
        description (str): One line saying when to use the skill
        visibility (Schema1123):
        collection_id (None | str): The collection the skill is in, or null at root
        collection_name (None | str): Name of that collection, or null at root
        content_bytes (float): Size of the Markdown body in bytes
        created_by_user_id (str):
        created_by_user_name (str): Display name of the creator, empty when no name is set or the account is removed
        created_by_user_email (str): Email of the creator, empty when the account is removed
        shared_with_user_ids (list[str]): IDs of the users the skill is shared with, any role
        shared_with_team_ids (list[str]): IDs of the teams the skill is shared with, any role
        maintainer_user_ids (list[str]): IDs of the users that maintain the skill: the same rights as the creator
        maintainer_team_ids (list[str]): IDs of the teams whose members maintain the skill
        collection_visibility (None | Schema1123): The collection's general access, null at root
        collection_shared_with_user_ids (list[str]): Users with access through the collection, any role
        collection_shared_with_team_ids (list[str]): Teams with access through the collection, any role
        collection_maintainer_user_ids (list[str]): Users that maintain the collection, and so this skill
        collection_maintainer_team_ids (list[str]): Teams that maintain the collection, and so this skill
        created_at (str):
        updated_at (str):
        content (str): The instructions as Markdown: the body of the SKILL.md without the frontmatter
        markdown (str): The whole skill as a SKILL.md document: name and description in the frontmatter, the
            instructions below. What the dashboard editor holds and what agents receive
        created_by_name (str): Display name of the creator, or their email when no name is set
    """

    id: str
    name: str
    description: str
    visibility: Schema1123
    collection_id: None | str
    collection_name: None | str
    content_bytes: float
    created_by_user_id: str
    created_by_user_name: str
    created_by_user_email: str
    shared_with_user_ids: list[str]
    shared_with_team_ids: list[str]
    maintainer_user_ids: list[str]
    maintainer_team_ids: list[str]
    collection_visibility: None | Schema1123
    collection_shared_with_user_ids: list[str]
    collection_shared_with_team_ids: list[str]
    collection_maintainer_user_ids: list[str]
    collection_maintainer_team_ids: list[str]
    created_at: str
    updated_at: str
    content: str
    markdown: str
    created_by_name: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        visibility = self.visibility.value

        collection_id: None | str
        collection_id = self.collection_id

        collection_name: None | str
        collection_name = self.collection_name

        content_bytes = self.content_bytes

        created_by_user_id = self.created_by_user_id

        created_by_user_name = self.created_by_user_name

        created_by_user_email = self.created_by_user_email

        shared_with_user_ids = self.shared_with_user_ids

        shared_with_team_ids = self.shared_with_team_ids

        maintainer_user_ids = self.maintainer_user_ids

        maintainer_team_ids = self.maintainer_team_ids

        collection_visibility: None | str
        if isinstance(self.collection_visibility, Schema1123):
            collection_visibility = self.collection_visibility.value
        else:
            collection_visibility = self.collection_visibility

        collection_shared_with_user_ids = self.collection_shared_with_user_ids

        collection_shared_with_team_ids = self.collection_shared_with_team_ids

        collection_maintainer_user_ids = self.collection_maintainer_user_ids

        collection_maintainer_team_ids = self.collection_maintainer_team_ids

        created_at = self.created_at

        updated_at = self.updated_at

        content = self.content

        markdown = self.markdown

        created_by_name = self.created_by_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "visibility": visibility,
                "collectionId": collection_id,
                "collectionName": collection_name,
                "contentBytes": content_bytes,
                "createdByUserId": created_by_user_id,
                "createdByUserName": created_by_user_name,
                "createdByUserEmail": created_by_user_email,
                "sharedWithUserIds": shared_with_user_ids,
                "sharedWithTeamIds": shared_with_team_ids,
                "maintainerUserIds": maintainer_user_ids,
                "maintainerTeamIds": maintainer_team_ids,
                "collectionVisibility": collection_visibility,
                "collectionSharedWithUserIds": collection_shared_with_user_ids,
                "collectionSharedWithTeamIds": collection_shared_with_team_ids,
                "collectionMaintainerUserIds": collection_maintainer_user_ids,
                "collectionMaintainerTeamIds": collection_maintainer_team_ids,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "content": content,
                "markdown": markdown,
                "createdByName": created_by_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        visibility = Schema1123(d.pop("visibility"))

        def _parse_collection_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        collection_id = _parse_collection_id(d.pop("collectionId"))

        def _parse_collection_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        collection_name = _parse_collection_name(d.pop("collectionName"))

        content_bytes = d.pop("contentBytes")

        created_by_user_id = d.pop("createdByUserId")

        created_by_user_name = d.pop("createdByUserName")

        created_by_user_email = d.pop("createdByUserEmail")

        shared_with_user_ids = cast(list[str], d.pop("sharedWithUserIds"))

        shared_with_team_ids = cast(list[str], d.pop("sharedWithTeamIds"))

        maintainer_user_ids = cast(list[str], d.pop("maintainerUserIds"))

        maintainer_team_ids = cast(list[str], d.pop("maintainerTeamIds"))

        def _parse_collection_visibility(data: object) -> None | Schema1123:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_schema1140_type_0 = Schema1123(data)

                return componentsschemas_schema1140_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Schema1123, data)

        collection_visibility = _parse_collection_visibility(d.pop("collectionVisibility"))

        collection_shared_with_user_ids = cast(list[str], d.pop("collectionSharedWithUserIds"))

        collection_shared_with_team_ids = cast(list[str], d.pop("collectionSharedWithTeamIds"))

        collection_maintainer_user_ids = cast(list[str], d.pop("collectionMaintainerUserIds"))

        collection_maintainer_team_ids = cast(list[str], d.pop("collectionMaintainerTeamIds"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        content = d.pop("content")

        markdown = d.pop("markdown")

        created_by_name = d.pop("createdByName")

        get_skill_response = cls(
            id=id,
            name=name,
            description=description,
            visibility=visibility,
            collection_id=collection_id,
            collection_name=collection_name,
            content_bytes=content_bytes,
            created_by_user_id=created_by_user_id,
            created_by_user_name=created_by_user_name,
            created_by_user_email=created_by_user_email,
            shared_with_user_ids=shared_with_user_ids,
            shared_with_team_ids=shared_with_team_ids,
            maintainer_user_ids=maintainer_user_ids,
            maintainer_team_ids=maintainer_team_ids,
            collection_visibility=collection_visibility,
            collection_shared_with_user_ids=collection_shared_with_user_ids,
            collection_shared_with_team_ids=collection_shared_with_team_ids,
            collection_maintainer_user_ids=collection_maintainer_user_ids,
            collection_maintainer_team_ids=collection_maintainer_team_ids,
            created_at=created_at,
            updated_at=updated_at,
            content=content,
            markdown=markdown,
            created_by_name=created_by_name,
        )

        return get_skill_response
