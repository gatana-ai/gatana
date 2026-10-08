from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema547")


@_attrs_define
class Schema547:
    """
    Attributes:
        issuer (str):
        authorize_endpoint (str):
        device_authorization_endpoint (str):
        token_endpoint (str):
        extra_authorization_parameters (str):
        supports_pkce (bool):
        supported_client_auth_methods (list[str]):
        supports_dynamic_client_registration (bool):
        service_documentation (str):
        metadata_url (str):
        available_scopes (list[str]):
        registration_endpoint (str | Unset):
        no_dynamic_client_registration_reason (None | str | Unset):
    """

    issuer: str
    authorize_endpoint: str
    device_authorization_endpoint: str
    token_endpoint: str
    extra_authorization_parameters: str
    supports_pkce: bool
    supported_client_auth_methods: list[str]
    supports_dynamic_client_registration: bool
    service_documentation: str
    metadata_url: str
    available_scopes: list[str]
    registration_endpoint: str | Unset = UNSET
    no_dynamic_client_registration_reason: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        issuer = self.issuer

        authorize_endpoint = self.authorize_endpoint

        device_authorization_endpoint = self.device_authorization_endpoint

        token_endpoint = self.token_endpoint

        extra_authorization_parameters = self.extra_authorization_parameters

        supports_pkce = self.supports_pkce

        supported_client_auth_methods = self.supported_client_auth_methods

        supports_dynamic_client_registration = self.supports_dynamic_client_registration

        service_documentation = self.service_documentation

        metadata_url = self.metadata_url

        available_scopes = self.available_scopes

        registration_endpoint = self.registration_endpoint

        no_dynamic_client_registration_reason: None | str | Unset
        if isinstance(self.no_dynamic_client_registration_reason, Unset):
            no_dynamic_client_registration_reason = UNSET
        else:
            no_dynamic_client_registration_reason = self.no_dynamic_client_registration_reason

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "issuer": issuer,
                "authorizeEndpoint": authorize_endpoint,
                "deviceAuthorizationEndpoint": device_authorization_endpoint,
                "tokenEndpoint": token_endpoint,
                "extraAuthorizationParameters": extra_authorization_parameters,
                "supportsPKCE": supports_pkce,
                "supportedClientAuthMethods": supported_client_auth_methods,
                "supportsDynamicClientRegistration": supports_dynamic_client_registration,
                "serviceDocumentation": service_documentation,
                "metadataUrl": metadata_url,
                "availableScopes": available_scopes,
            }
        )
        if registration_endpoint is not UNSET:
            field_dict["registrationEndpoint"] = registration_endpoint
        if no_dynamic_client_registration_reason is not UNSET:
            field_dict["noDynamicClientRegistrationReason"] = no_dynamic_client_registration_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        issuer = d.pop("issuer")

        authorize_endpoint = d.pop("authorizeEndpoint")

        device_authorization_endpoint = d.pop("deviceAuthorizationEndpoint")

        token_endpoint = d.pop("tokenEndpoint")

        extra_authorization_parameters = d.pop("extraAuthorizationParameters")

        supports_pkce = d.pop("supportsPKCE")

        supported_client_auth_methods = cast(list[str], d.pop("supportedClientAuthMethods"))

        supports_dynamic_client_registration = d.pop("supportsDynamicClientRegistration")

        service_documentation = d.pop("serviceDocumentation")

        metadata_url = d.pop("metadataUrl")

        available_scopes = cast(list[str], d.pop("availableScopes"))

        registration_endpoint = d.pop("registrationEndpoint", UNSET)

        def _parse_no_dynamic_client_registration_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        no_dynamic_client_registration_reason = _parse_no_dynamic_client_registration_reason(
            d.pop("noDynamicClientRegistrationReason", UNSET)
        )

        schema_547 = cls(
            issuer=issuer,
            authorize_endpoint=authorize_endpoint,
            device_authorization_endpoint=device_authorization_endpoint,
            token_endpoint=token_endpoint,
            extra_authorization_parameters=extra_authorization_parameters,
            supports_pkce=supports_pkce,
            supported_client_auth_methods=supported_client_auth_methods,
            supports_dynamic_client_registration=supports_dynamic_client_registration,
            service_documentation=service_documentation,
            metadata_url=metadata_url,
            available_scopes=available_scopes,
            registration_endpoint=registration_endpoint,
            no_dynamic_client_registration_reason=no_dynamic_client_registration_reason,
        )

        return schema_547
