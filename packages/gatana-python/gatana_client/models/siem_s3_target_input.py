from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schema_260 import Schema260
from ..types import UNSET, Unset

T = TypeVar("T", bound="SiemS3TargetInput")


@_attrs_define
class SiemS3TargetInput:
    """
    Attributes:
        kind (Literal['s3']):
        bucket (str): Bucket name
        access_key_id (str): Access key ID with permission to write under the prefix
        prefix (str | Unset):
        region (str | Unset):
        endpoint (None | str | Unset):
        force_path_style (bool | Unset):
        secret_access_key (str | Unset):
        compression (Schema260 | Unset):
    """

    kind: Literal["s3"]
    bucket: str
    access_key_id: str
    prefix: str | Unset = UNSET
    region: str | Unset = UNSET
    endpoint: None | str | Unset = UNSET
    force_path_style: bool | Unset = UNSET
    secret_access_key: str | Unset = UNSET
    compression: Schema260 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        bucket = self.bucket

        access_key_id = self.access_key_id

        prefix = self.prefix

        region = self.region

        endpoint: None | str | Unset
        if isinstance(self.endpoint, Unset):
            endpoint = UNSET
        else:
            endpoint = self.endpoint

        force_path_style = self.force_path_style

        secret_access_key = self.secret_access_key

        compression: str | Unset = UNSET
        if not isinstance(self.compression, Unset):
            compression = self.compression.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "bucket": bucket,
                "accessKeyId": access_key_id,
            }
        )
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if region is not UNSET:
            field_dict["region"] = region
        if endpoint is not UNSET:
            field_dict["endpoint"] = endpoint
        if force_path_style is not UNSET:
            field_dict["forcePathStyle"] = force_path_style
        if secret_access_key is not UNSET:
            field_dict["secretAccessKey"] = secret_access_key
        if compression is not UNSET:
            field_dict["compression"] = compression

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = cast(Literal["s3"], d.pop("kind"))
        if kind != "s3":
            raise ValueError(f"kind must match const 's3', got '{kind}'")

        bucket = d.pop("bucket")

        access_key_id = d.pop("accessKeyId")

        prefix = d.pop("prefix", UNSET)

        region = d.pop("region", UNSET)

        def _parse_endpoint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        endpoint = _parse_endpoint(d.pop("endpoint", UNSET))

        force_path_style = d.pop("forcePathStyle", UNSET)

        secret_access_key = d.pop("secretAccessKey", UNSET)

        _compression = d.pop("compression", UNSET)
        compression: Schema260 | Unset
        if isinstance(_compression, Unset):
            compression = UNSET
        else:
            compression = Schema260(_compression)

        siem_s3_target_input = cls(
            kind=kind,
            bucket=bucket,
            access_key_id=access_key_id,
            prefix=prefix,
            region=region,
            endpoint=endpoint,
            force_path_style=force_path_style,
            secret_access_key=secret_access_key,
            compression=compression,
        )

        siem_s3_target_input.additional_properties = d
        return siem_s3_target_input

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
