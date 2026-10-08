from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Schema122AsType0")


@_attrs_define
class Schema122AsType0:
    """
    Attributes:
        issuer (str | Unset):
        authorize_endpoint (str | Unset):
        device_authorization_endpoint (str | Unset):
        token_endpoint (str | Unset):
        extra_authorization_parameters (str | Unset):
        registration_endpoint (str | Unset):
        supports_pkce (bool | Unset):
        supported_client_auth_methods (list[str] | Unset):
        supports_dynamic_client_registration (bool | Unset):
        no_dynamic_client_registration_reason (None | str | Unset):
        service_documentation (str | Unset):
        metadata_url (str | Unset):
        available_scopes (list[str] | Unset):
    """

    issuer: str | Unset = UNSET
    authorize_endpoint: str | Unset = UNSET
    device_authorization_endpoint: str | Unset = UNSET
    token_endpoint: str | Unset = UNSET
    extra_authorization_parameters: str | Unset = UNSET
    registration_endpoint: str | Unset = UNSET
    supports_pkce: bool | Unset = UNSET
    supported_client_auth_methods: list[str] | Unset = UNSET
    supports_dynamic_client_registration: bool | Unset = UNSET
    no_dynamic_client_registration_reason: None | str | Unset = UNSET
    service_documentation: str | Unset = UNSET
    metadata_url: str | Unset = UNSET
    available_scopes: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        issuer = self.issuer

        authorize_endpoint = self.authorize_endpoint

        device_authorization_endpoint = self.device_authorization_endpoint

        token_endpoint = self.token_endpoint

        extra_authorization_parameters = self.extra_authorization_parameters

        registration_endpoint = self.registration_endpoint

        supports_pkce = self.supports_pkce

        supported_client_auth_methods: list[str] | Unset = UNSET
        if not isinstance(self.supported_client_auth_methods, Unset):
            supported_client_auth_methods = self.supported_client_auth_methods

        supports_dynamic_client_registration = self.supports_dynamic_client_registration

        no_dynamic_client_registration_reason: None | str | Unset
        if isinstance(self.no_dynamic_client_registration_reason, Unset):
            no_dynamic_client_registration_reason = UNSET
        else:
            no_dynamic_client_registration_reason = self.no_dynamic_client_registration_reason

        service_documentation = self.service_documentation

        metadata_url = self.metadata_url

        available_scopes: list[str] | Unset = UNSET
        if not isinstance(self.available_scopes, Unset):
            available_scopes = self.available_scopes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if issuer is not UNSET:
            field_dict["issuer"] = issuer
        if authorize_endpoint is not UNSET:
            field_dict["authorizeEndpoint"] = authorize_endpoint
        if device_authorization_endpoint is not UNSET:
            field_dict["deviceAuthorizationEndpoint"] = device_authorization_endpoint
        if token_endpoint is not UNSET:
            field_dict["tokenEndpoint"] = token_endpoint
        if extra_authorization_parameters is not UNSET:
            field_dict["extraAuthorizationParameters"] = extra_authorization_parameters
        if registration_endpoint is not UNSET:
            field_dict["registrationEndpoint"] = registration_endpoint
        if supports_pkce is not UNSET:
            field_dict["supportsPKCE"] = supports_pkce
        if supported_client_auth_methods is not UNSET:
            field_dict["supportedClientAuthMethods"] = supported_client_auth_methods
        if supports_dynamic_client_registration is not UNSET:
            field_dict["supportsDynamicClientRegistration"] = supports_dynamic_client_registration
        if no_dynamic_client_registration_reason is not UNSET:
            field_dict["noDynamicClientRegistrationReason"] = no_dynamic_client_registration_reason
        if service_documentation is not UNSET:
            field_dict["serviceDocumentation"] = service_documentation
        if metadata_url is not UNSET:
            field_dict["metadataUrl"] = metadata_url
        if available_scopes is not UNSET:
            field_dict["availableScopes"] = available_scopes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        issuer = d.pop("issuer", UNSET)

        authorize_endpoint = d.pop("authorizeEndpoint", UNSET)

        device_authorization_endpoint = d.pop("deviceAuthorizationEndpoint", UNSET)

        token_endpoint = d.pop("tokenEndpoint", UNSET)

        extra_authorization_parameters = d.pop("extraAuthorizationParameters", UNSET)

        registration_endpoint = d.pop("registrationEndpoint", UNSET)

        supports_pkce = d.pop("supportsPKCE", UNSET)

        supported_client_auth_methods = cast(list[str], d.pop("supportedClientAuthMethods", UNSET))

        supports_dynamic_client_registration = d.pop("supportsDynamicClientRegistration", UNSET)

        def _parse_no_dynamic_client_registration_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        no_dynamic_client_registration_reason = _parse_no_dynamic_client_registration_reason(
            d.pop("noDynamicClientRegistrationReason", UNSET)
        )

        service_documentation = d.pop("serviceDocumentation", UNSET)

        metadata_url = d.pop("metadataUrl", UNSET)

        available_scopes = cast(list[str], d.pop("availableScopes", UNSET))

        schema_122_as_type_0 = cls(
            issuer=issuer,
            authorize_endpoint=authorize_endpoint,
            device_authorization_endpoint=device_authorization_endpoint,
            token_endpoint=token_endpoint,
            extra_authorization_parameters=extra_authorization_parameters,
            registration_endpoint=registration_endpoint,
            supports_pkce=supports_pkce,
            supported_client_auth_methods=supported_client_auth_methods,
            supports_dynamic_client_registration=supports_dynamic_client_registration,
            no_dynamic_client_registration_reason=no_dynamic_client_registration_reason,
            service_documentation=service_documentation,
            metadata_url=metadata_url,
            available_scopes=available_scopes,
        )

        schema_122_as_type_0.additional_properties = d
        return schema_122_as_type_0

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
