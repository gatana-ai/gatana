from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_secret_store_body_type import CreateSecretStoreBodyType

if TYPE_CHECKING:
    from ..models.aws_secrets_manager_configuration import AwsSecretsManagerConfiguration
    from ..models.azure_key_vault_configuration import AzureKeyVaultConfiguration
    from ..models.gcp_secret_manager_configuration import GcpSecretManagerConfiguration
    from ..models.hashi_corp_vault_configuration import HashiCorpVaultConfiguration
    from ..models.infisical_configuration import InfisicalConfiguration


T = TypeVar("T", bound="CreateSecretStoreBody")


@_attrs_define
class CreateSecretStoreBody:
    """
    Attributes:
        name (str):
        type_ (CreateSecretStoreBodyType):
        configuration (AwsSecretsManagerConfiguration | AzureKeyVaultConfiguration | GcpSecretManagerConfiguration |
            HashiCorpVaultConfiguration | InfisicalConfiguration):
    """

    name: str
    type_: CreateSecretStoreBodyType
    configuration: (
        AwsSecretsManagerConfiguration
        | AzureKeyVaultConfiguration
        | GcpSecretManagerConfiguration
        | HashiCorpVaultConfiguration
        | InfisicalConfiguration
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.aws_secrets_manager_configuration import AwsSecretsManagerConfiguration
        from ..models.gcp_secret_manager_configuration import GcpSecretManagerConfiguration
        from ..models.hashi_corp_vault_configuration import HashiCorpVaultConfiguration
        from ..models.infisical_configuration import InfisicalConfiguration

        name = self.name

        type_ = self.type_.value

        configuration: dict[str, Any]
        if isinstance(self.configuration, AwsSecretsManagerConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, GcpSecretManagerConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, HashiCorpVaultConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, InfisicalConfiguration):
            configuration = self.configuration.to_dict()
        else:
            configuration = self.configuration.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
                "configuration": configuration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.aws_secrets_manager_configuration import AwsSecretsManagerConfiguration
        from ..models.azure_key_vault_configuration import AzureKeyVaultConfiguration
        from ..models.gcp_secret_manager_configuration import GcpSecretManagerConfiguration
        from ..models.hashi_corp_vault_configuration import HashiCorpVaultConfiguration
        from ..models.infisical_configuration import InfisicalConfiguration

        d = dict(src_dict)
        name = d.pop("name")

        type_ = CreateSecretStoreBodyType(d.pop("type"))

        def _parse_configuration(
            data: object,
        ) -> (
            AwsSecretsManagerConfiguration
            | AzureKeyVaultConfiguration
            | GcpSecretManagerConfiguration
            | HashiCorpVaultConfiguration
            | InfisicalConfiguration
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema217_type_0 = AwsSecretsManagerConfiguration.from_dict(data)

                return componentsschemas_schema217_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema217_type_1 = GcpSecretManagerConfiguration.from_dict(data)

                return componentsschemas_schema217_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema217_type_2 = HashiCorpVaultConfiguration.from_dict(data)

                return componentsschemas_schema217_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_schema217_type_3 = InfisicalConfiguration.from_dict(data)

                return componentsschemas_schema217_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_schema217_type_4 = AzureKeyVaultConfiguration.from_dict(data)

            return componentsschemas_schema217_type_4

        configuration = _parse_configuration(d.pop("configuration"))

        create_secret_store_body = cls(
            name=name,
            type_=type_,
            configuration=configuration,
        )

        create_secret_store_body.additional_properties = d
        return create_secret_store_body

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
