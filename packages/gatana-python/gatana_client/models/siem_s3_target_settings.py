from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_1033 import Schema1033

T = TypeVar("T", bound="SiemS3TargetSettings")


@_attrs_define
class SiemS3TargetSettings:
    """
    Attributes:
        kind (Literal['s3']): Write batches to an S3 bucket
        bucket (str): Bucket name
        prefix (str): Object key prefix; empty or ending in a slash
        region (str): Bucket region, e.g. eu-west-1
        endpoint (None | str): Custom endpoint of an S3-compatible store, or null for Amazon S3
        force_path_style (bool): Whether to address the bucket in the path instead of the host
        access_key_id (str): Access key ID used for uploads; the secret key is never returned
        compression (Schema1033):
    """

    kind: Literal["s3"]
    bucket: str
    prefix: str
    region: str
    endpoint: None | str
    force_path_style: bool
    access_key_id: str
    compression: Schema1033

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        bucket = self.bucket

        prefix = self.prefix

        region = self.region

        endpoint: None | str
        endpoint = self.endpoint

        force_path_style = self.force_path_style

        access_key_id = self.access_key_id

        compression = self.compression.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "bucket": bucket,
                "prefix": prefix,
                "region": region,
                "endpoint": endpoint,
                "forcePathStyle": force_path_style,
                "accessKeyId": access_key_id,
                "compression": compression,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = cast(Literal["s3"], d.pop("kind"))
        if kind != "s3":
            raise ValueError(f"kind must match const 's3', got '{kind}'")

        bucket = d.pop("bucket")

        prefix = d.pop("prefix")

        region = d.pop("region")

        def _parse_endpoint(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        endpoint = _parse_endpoint(d.pop("endpoint"))

        force_path_style = d.pop("forcePathStyle")

        access_key_id = d.pop("accessKeyId")

        compression = Schema1033(d.pop("compression"))

        siem_s3_target_settings = cls(
            kind=kind,
            bucket=bucket,
            prefix=prefix,
            region=region,
            endpoint=endpoint,
            force_path_style=force_path_style,
            access_key_id=access_key_id,
            compression=compression,
        )

        return siem_s3_target_settings
