from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_260 import Schema260
from ..types import UNSET, Unset

T = TypeVar("T", bound="SiemGcsTargetInput")


@_attrs_define
class SiemGcsTargetInput:
    """
    Attributes:
        kind (Literal['gcs']):
        bucket (str): Bucket name
        prefix (str | Unset):
        service_account_key (str | Unset):
        compression (Schema260 | Unset):
    """

    kind: Literal["gcs"]
    bucket: str
    prefix: str | Unset = UNSET
    service_account_key: str | Unset = UNSET
    compression: Schema260 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        bucket = self.bucket

        prefix = self.prefix

        service_account_key = self.service_account_key

        compression: str | Unset = UNSET
        if not isinstance(self.compression, Unset):
            compression = self.compression.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "bucket": bucket,
            }
        )
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if service_account_key is not UNSET:
            field_dict["serviceAccountKey"] = service_account_key
        if compression is not UNSET:
            field_dict["compression"] = compression

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = cast(Literal["gcs"], d.pop("kind"))
        if kind != "gcs":
            raise ValueError(f"kind must match const 'gcs', got '{kind}'")

        bucket = d.pop("bucket")

        prefix = d.pop("prefix", UNSET)

        service_account_key = d.pop("serviceAccountKey", UNSET)

        _compression = d.pop("compression", UNSET)
        compression: Schema260 | Unset
        if isinstance(_compression, Unset):
            compression = UNSET
        else:
            compression = Schema260(_compression)

        siem_gcs_target_input = cls(
            kind=kind,
            bucket=bucket,
            prefix=prefix,
            service_account_key=service_account_key,
            compression=compression,
        )

        siem_gcs_target_input.additional_properties = d
        return siem_gcs_target_input

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
