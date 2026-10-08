from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.profile_team_assignment import ProfileTeamAssignment


T = TypeVar("T", bound="Schema913")


@_attrs_define
class Schema913:
    """
    Attributes:
        profile_assignments (list[ProfileTeamAssignment]): Profile assignments of the team
    """

    profile_assignments: list[ProfileTeamAssignment]

    def to_dict(self) -> dict[str, Any]:
        profile_assignments = []
        for profile_assignments_item_data in self.profile_assignments:
            profile_assignments_item = profile_assignments_item_data.to_dict()
            profile_assignments.append(profile_assignments_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "profileAssignments": profile_assignments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_team_assignment import ProfileTeamAssignment

        d = dict(src_dict)
        profile_assignments = []
        _profile_assignments = d.pop("profileAssignments")
        for profile_assignments_item_data in _profile_assignments:
            profile_assignments_item = ProfileTeamAssignment.from_dict(profile_assignments_item_data)

            profile_assignments.append(profile_assignments_item)

        schema_913 = cls(
            profile_assignments=profile_assignments,
        )

        return schema_913
