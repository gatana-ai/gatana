from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_1040 import Schema1040

T = TypeVar("T", bound="SiemGcsTargetSettings")


@_attrs_define
class SiemGcsTargetSettings:
    """
    Attributes:
        kind (Literal['gcs']): Write batches to a Google Cloud Storage bucket
        bucket (str): Bucket name
        prefix (str): Object name prefix; empty or ending in a slash
        service_account_email (str): Service account email; its key is never returned
        project_id (str): Project the service account belongs to
        compression (Schema1040):
    """

    kind: Literal["gcs"]
    bucket: str
    prefix: str
    service_account_email: str
    project_id: str
    compression: Schema1040

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        bucket = self.bucket

        prefix = self.prefix

        service_account_email = self.service_account_email

        project_id = self.project_id

        compression = self.compression.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "bucket": bucket,
                "prefix": prefix,
                "serviceAccountEmail": service_account_email,
                "projectId": project_id,
                "compression": compression,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = cast(Literal["gcs"], d.pop("kind"))
        if kind != "gcs":
            raise ValueError(f"kind must match const 'gcs', got '{kind}'")

        bucket = d.pop("bucket")

        prefix = d.pop("prefix")

        service_account_email = d.pop("serviceAccountEmail")

        project_id = d.pop("projectId")

        compression = Schema1040(d.pop("compression"))

        siem_gcs_target_settings = cls(
            kind=kind,
            bucket=bucket,
            prefix=prefix,
            service_account_email=service_account_email,
            project_id=project_id,
            compression=compression,
        )

        return siem_gcs_target_settings
