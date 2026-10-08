from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_1123 import Schema1123

T = TypeVar("T", bound="SkillCollectionDto")


@_attrs_define
class SkillCollectionDto:
    """
    Attributes:
        id (str):
        name (str): Unique name in the organization; what the CLI subscribes to
        description (str): One line saying what the collection gathers
        visibility (Schema1123):
        created_by_user_id (str):
        created_by_user_name (str): Display name of the creator, empty when no name is set or the account is removed
        created_by_user_email (str): Email of the creator, empty when the account is removed
        shared_with_user_ids (list[str]): IDs of the users the collection is shared with, any role
        shared_with_team_ids (list[str]): IDs of the teams the collection is shared with, any role
        maintainer_user_ids (list[str]): IDs of the users that maintain the collection
        maintainer_team_ids (list[str]): IDs of the teams whose members maintain the collection
        skill_count (float): How many skills in it the caller can read
        created_at (str):
        updated_at (str):
    """

    id: str
    name: str
    description: str
    visibility: Schema1123
    created_by_user_id: str
    created_by_user_name: str
    created_by_user_email: str
    shared_with_user_ids: list[str]
    shared_with_team_ids: list[str]
    maintainer_user_ids: list[str]
    maintainer_team_ids: list[str]
    skill_count: float
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        visibility = self.visibility.value

        created_by_user_id = self.created_by_user_id

        created_by_user_name = self.created_by_user_name

        created_by_user_email = self.created_by_user_email

        shared_with_user_ids = self.shared_with_user_ids

        shared_with_team_ids = self.shared_with_team_ids

        maintainer_user_ids = self.maintainer_user_ids

        maintainer_team_ids = self.maintainer_team_ids

        skill_count = self.skill_count

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "visibility": visibility,
                "createdByUserId": created_by_user_id,
                "createdByUserName": created_by_user_name,
                "createdByUserEmail": created_by_user_email,
                "sharedWithUserIds": shared_with_user_ids,
                "sharedWithTeamIds": shared_with_team_ids,
                "maintainerUserIds": maintainer_user_ids,
                "maintainerTeamIds": maintainer_team_ids,
                "skillCount": skill_count,
                "createdAt": created_at,
                "updatedAt": updated_at,
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

        created_by_user_id = d.pop("createdByUserId")

        created_by_user_name = d.pop("createdByUserName")

        created_by_user_email = d.pop("createdByUserEmail")

        shared_with_user_ids = cast(list[str], d.pop("sharedWithUserIds"))

        shared_with_team_ids = cast(list[str], d.pop("sharedWithTeamIds"))

        maintainer_user_ids = cast(list[str], d.pop("maintainerUserIds"))

        maintainer_team_ids = cast(list[str], d.pop("maintainerTeamIds"))

        skill_count = d.pop("skillCount")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        skill_collection_dto = cls(
            id=id,
            name=name,
            description=description,
            visibility=visibility,
            created_by_user_id=created_by_user_id,
            created_by_user_name=created_by_user_name,
            created_by_user_email=created_by_user_email,
            shared_with_user_ids=shared_with_user_ids,
            shared_with_team_ids=shared_with_team_ids,
            maintainer_user_ids=maintainer_user_ids,
            maintainer_team_ids=maintainer_team_ids,
            skill_count=skill_count,
            created_at=created_at,
            updated_at=updated_at,
        )

        return skill_collection_dto
