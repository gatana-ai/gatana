from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_923 import Schema923

if TYPE_CHECKING:
    from ..models.aws_secrets_manager_configuration_output import AwsSecretsManagerConfigurationOutput
    from ..models.azure_key_vault_configuration_output import AzureKeyVaultConfigurationOutput
    from ..models.gcp_secret_manager_configuration_output import GcpSecretManagerConfigurationOutput
    from ..models.hashi_corp_vault_configuration_output import HashiCorpVaultConfigurationOutput
    from ..models.infisical_configuration_output import InfisicalConfigurationOutput


T = TypeVar("T", bound="SecretStoreDetailResponse")


@_attrs_define
class SecretStoreDetailResponse:
    """
    Attributes:
        id (str):
        name (str):
        type_ (Schema923):
        is_enabled (bool):
        created_at (str):
        updated_at (str):
        configuration (AwsSecretsManagerConfigurationOutput | AzureKeyVaultConfigurationOutput |
            GcpSecretManagerConfigurationOutput | HashiCorpVaultConfigurationOutput | InfisicalConfigurationOutput):
    """

    id: str
    name: str
    type_: Schema923
    is_enabled: bool
    created_at: str
    updated_at: str
    configuration: (
        AwsSecretsManagerConfigurationOutput
        | AzureKeyVaultConfigurationOutput
        | GcpSecretManagerConfigurationOutput
        | HashiCorpVaultConfigurationOutput
        | InfisicalConfigurationOutput
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.aws_secrets_manager_configuration_output import AwsSecretsManagerConfigurationOutput
        from ..models.gcp_secret_manager_configuration_output import GcpSecretManagerConfigurationOutput
        from ..models.hashi_corp_vault_configuration_output import HashiCorpVaultConfigurationOutput
        from ..models.infisical_configuration_output import InfisicalConfigurationOutput

        id = self.id

        name = self.name

        type_ = self.type_.value

        is_enabled = self.is_enabled

        created_at = self.created_at

        updated_at = self.updated_at

        configuration: dict[str, Any]
        if isinstance(self.configuration, AwsSecretsManagerConfigurationOutput):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, GcpSecretManagerConfigurationOutput):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, HashiCorpVaultConfigurationOutput):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, InfisicalConfigurationOutput):
            configuration = self.configuration.to_dict()
        else:
            configuration = self.configuration.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "type": type_,
                "isEnabled": is_enabled,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "configuration": configuration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.aws_secrets_manager_configuration_output import AwsSecretsManagerConfigurationOutput
        from ..models.azure_key_vault_configuration_output import AzureKeyVaultConfigurationOutput
        from ..models.gcp_secret_manager_configuration_output import GcpSecretManagerConfigurationOutput
        from ..models.hashi_corp_vault_configuration_output import HashiCorpVaultConfigurationOutput
        from ..models.infisical_configuration_output import InfisicalConfigurationOutput

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        type_ = Schema923(d.pop("type"))

        is_enabled = d.pop("isEnabled")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        def _parse_configuration(
            data: object,
        ) -> (
            AwsSecretsManagerConfigurationOutput
            | AzureKeyVaultConfigurationOutput
            | GcpSecretManagerConfigurationOutput
            | HashiCorpVaultConfigurationOutput
            | InfisicalConfigurationOutput
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema927_type_0 = AwsSecretsManagerConfigurationOutput.from_dict(data)

                return componentsschemas_schema927_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema927_type_1 = GcpSecretManagerConfigurationOutput.from_dict(data)

                return componentsschemas_schema927_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema927_type_2 = HashiCorpVaultConfigurationOutput.from_dict(data)

                return componentsschemas_schema927_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema927_type_3 = InfisicalConfigurationOutput.from_dict(data)

                return componentsschemas_schema927_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_schema927_type_4 = AzureKeyVaultConfigurationOutput.from_dict(data)

            return componentsschemas_schema927_type_4

        configuration = _parse_configuration(d.pop("configuration"))

        secret_store_detail_response = cls(
            id=id,
            name=name,
            type_=type_,
            is_enabled=is_enabled,
            created_at=created_at,
            updated_at=updated_at,
            configuration=configuration,
        )

        return secret_store_detail_response
