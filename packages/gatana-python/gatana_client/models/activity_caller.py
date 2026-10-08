from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_392 import Schema392

T = TypeVar("T", bound="ActivityCaller")


@_attrs_define
class ActivityCaller:
    """
    Attributes:
        id (str): Client ID of an OAuth client, or ID of a personal access token
        kind (Schema392): Which of the two the ID names
        label (str): How the caller reads to a person; the ID when it has no name
        count (float): Tool calls made through that caller
    """

    id: str
    kind: Schema392
    label: str
    count: float

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        kind = self.kind.value

        label = self.label

        count = self.count

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "kind": kind,
                "label": label,
                "count": count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        kind = Schema392(d.pop("kind"))

        label = d.pop("label")

        count = d.pop("count")

        activity_caller = cls(
            id=id,
            kind=kind,
            label=label,
            count=count,
        )

        return activity_caller
