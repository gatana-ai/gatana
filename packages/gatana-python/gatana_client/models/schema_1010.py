from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_633 import Schema633

if TYPE_CHECKING:
    from ..models.schema_462 import Schema462
    from ..models.server_credentials_dto import ServerCredentialsDto


T = TypeVar("T", bound="Schema1010")


@_attrs_define
class Schema1010:
    """
    Attributes:
        name (str): Name of the server; currently the same value as slug
        slug (str): URL-friendly name of the server, unique within the tenant
        authorization (Schema462):
        credentials_num_keys (float | None): Number of API keys the server expects, or null when the server does not use
            API key authorization
        credential_scope (Schema633):
        credentials (None | ServerCredentialsDto): Credentials stored for the server in this profile, or null if none
    """

    name: str
    slug: str
    authorization: Schema462
    credentials_num_keys: float | None
    credential_scope: Schema633
    credentials: None | ServerCredentialsDto

    def to_dict(self) -> dict[str, Any]:
        from ..models.server_credentials_dto import ServerCredentialsDto

        name = self.name

        slug = self.slug

        authorization = self.authorization.to_dict()

        credentials_num_keys: float | None
        credentials_num_keys = self.credentials_num_keys

        credential_scope = self.credential_scope.value

        credentials: dict[str, Any] | None
        if isinstance(self.credentials, ServerCredentialsDto):
            credentials = self.credentials.to_dict()
        else:
            credentials = self.credentials

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "slug": slug,
                "authorization": authorization,
                "credentialsNumKeys": credentials_num_keys,
                "credentialScope": credential_scope,
                "credentials": credentials,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_462 import Schema462
        from ..models.server_credentials_dto import ServerCredentialsDto

        d = dict(src_dict)
        name = d.pop("name")

        slug = d.pop("slug")

        authorization = Schema462.from_dict(d.pop("authorization"))

        def _parse_credentials_num_keys(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        credentials_num_keys = _parse_credentials_num_keys(d.pop("credentialsNumKeys"))

        credential_scope = Schema633(d.pop("credentialScope"))

        def _parse_credentials(data: object) -> None | ServerCredentialsDto:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                credentials_type_0 = ServerCredentialsDto.from_dict(data)

                return credentials_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServerCredentialsDto, data)

        credentials = _parse_credentials(d.pop("credentials"))

        schema_1010 = cls(
            name=name,
            slug=slug,
            authorization=authorization,
            credentials_num_keys=credentials_num_keys,
            credential_scope=credential_scope,
            credentials=credentials,
        )

        return schema_1010
