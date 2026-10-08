from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="ServerFile")


@_attrs_define
class ServerFile:
    """
    Attributes:
        tenant_id (str): ID of the tenant that owns the file
        server_id (str): ID of the server that the file belongs to
        id (str): Unique ID of the file record
        filename (str): Name of the file as exposed to the server
        source_type (Literal['aws-secrets-manager'] | Literal['aws-ssm'] | Literal['gcs'] | Literal['s3']): Backing
            store that holds the file content
        source_id (str): Identifier of the file in the backing store
        size (float | None): File size in bytes, or null if unknown
        credential_id (None | str): ID of the credential used to read the file, or null
        created_at (str): Time when the file record was created
        updated_at (str): Time when the file record was last updated
    """

    tenant_id: str
    server_id: str
    id: str
    filename: str
    source_type: Literal["aws-secrets-manager"] | Literal["aws-ssm"] | Literal["gcs"] | Literal["s3"]
    source_id: str
    size: float | None
    credential_id: None | str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        server_id = self.server_id

        id = self.id

        filename = self.filename

        source_type: Literal["aws-secrets-manager"] | Literal["aws-ssm"] | Literal["gcs"] | Literal["s3"]
        source_type = self.source_type

        source_id = self.source_id

        size: float | None
        size = self.size

        credential_id: None | str
        credential_id = self.credential_id

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tenantId": tenant_id,
                "serverId": server_id,
                "id": id,
                "filename": filename,
                "sourceType": source_type,
                "sourceId": source_id,
                "size": size,
                "credentialId": credential_id,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = d.pop("tenantId")

        server_id = d.pop("serverId")

        id = d.pop("id")

        filename = d.pop("filename")

        def _parse_source_type(
            data: object,
        ) -> Literal["aws-secrets-manager"] | Literal["aws-ssm"] | Literal["gcs"] | Literal["s3"]:
            componentsschemas_schema583_type_0 = cast(Literal["gcs"], data)
            if componentsschemas_schema583_type_0 != "gcs":
                raise ValueError(
                    f"/components/schemas/__schema583_type_0 must match const 'gcs', got '{componentsschemas_schema583_type_0}'"
                )
            return componentsschemas_schema583_type_0
            componentsschemas_schema583_type_1 = cast(Literal["s3"], data)
            if componentsschemas_schema583_type_1 != "s3":
                raise ValueError(
                    f"/components/schemas/__schema583_type_1 must match const 's3', got '{componentsschemas_schema583_type_1}'"
                )
            return componentsschemas_schema583_type_1
            componentsschemas_schema583_type_2 = cast(Literal["aws-ssm"], data)
            if componentsschemas_schema583_type_2 != "aws-ssm":
                raise ValueError(
                    f"/components/schemas/__schema583_type_2 must match const 'aws-ssm', got '{componentsschemas_schema583_type_2}'"
                )
            return componentsschemas_schema583_type_2
            componentsschemas_schema583_type_3 = cast(Literal["aws-secrets-manager"], data)
            if componentsschemas_schema583_type_3 != "aws-secrets-manager":
                raise ValueError(
                    f"/components/schemas/__schema583_type_3 must match const 'aws-secrets-manager', got '{componentsschemas_schema583_type_3}'"
                )
            return componentsschemas_schema583_type_3

        source_type = _parse_source_type(d.pop("sourceType"))

        source_id = d.pop("sourceId")

        def _parse_size(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        size = _parse_size(d.pop("size"))

        def _parse_credential_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        credential_id = _parse_credential_id(d.pop("credentialId"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        server_file = cls(
            tenant_id=tenant_id,
            server_id=server_id,
            id=id,
            filename=filename,
            source_type=source_type,
            source_id=source_id,
            size=size,
            credential_id=credential_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        return server_file
