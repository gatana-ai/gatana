from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.schema_682 import Schema682

T = TypeVar("T", bound="TenantOidcConfiguration")


@_attrs_define
class TenantOidcConfiguration:
    """
    Attributes:
        is_enabled (bool): Whether sign-in through the OIDC provider is enabled
        display_name (str): Display name of the identity provider shown on the sign-in page
        issuer (str): Issuer identifier of the OIDC provider
        authorize_endpoint (str): URL of the authorization endpoint
        extra_parameters (str): Extra query parameters to add to the authorization request
        token_endpoint (str): URL of the token endpoint
        user_info_endpoint (str): URL of the userinfo endpoint
        introspection_endpoint (str): URL of the token introspection endpoint
        jwks_uri (str): URL of the JSON Web Key Set
        client_id (str): OAuth client ID
        client_secret (str): OAuth client secret
        client_auth_method (Schema682): Client authentication method used at the token endpoint
        scopes (str): Space-separated OAuth scopes to request
    """

    is_enabled: bool
    display_name: str
    issuer: str
    authorize_endpoint: str
    extra_parameters: str
    token_endpoint: str
    user_info_endpoint: str
    introspection_endpoint: str
    jwks_uri: str
    client_id: str
    client_secret: str
    client_auth_method: Schema682
    scopes: str

    def to_dict(self) -> dict[str, Any]:
        is_enabled = self.is_enabled

        display_name = self.display_name

        issuer = self.issuer

        authorize_endpoint = self.authorize_endpoint

        extra_parameters = self.extra_parameters

        token_endpoint = self.token_endpoint

        user_info_endpoint = self.user_info_endpoint

        introspection_endpoint = self.introspection_endpoint

        jwks_uri = self.jwks_uri

        client_id = self.client_id

        client_secret = self.client_secret

        client_auth_method = self.client_auth_method.value

        scopes = self.scopes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "isEnabled": is_enabled,
                "displayName": display_name,
                "issuer": issuer,
                "authorizeEndpoint": authorize_endpoint,
                "extraParameters": extra_parameters,
                "tokenEndpoint": token_endpoint,
                "userInfoEndpoint": user_info_endpoint,
                "introspectionEndpoint": introspection_endpoint,
                "jwksUri": jwks_uri,
                "clientId": client_id,
                "clientSecret": client_secret,
                "clientAuthMethod": client_auth_method,
                "scopes": scopes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_enabled = d.pop("isEnabled")

        display_name = d.pop("displayName")

        issuer = d.pop("issuer")

        authorize_endpoint = d.pop("authorizeEndpoint")

        extra_parameters = d.pop("extraParameters")

        token_endpoint = d.pop("tokenEndpoint")

        user_info_endpoint = d.pop("userInfoEndpoint")

        introspection_endpoint = d.pop("introspectionEndpoint")

        jwks_uri = d.pop("jwksUri")

        client_id = d.pop("clientId")

        client_secret = d.pop("clientSecret")

        client_auth_method = Schema682(d.pop("clientAuthMethod"))

        scopes = d.pop("scopes")

        tenant_oidc_configuration = cls(
            is_enabled=is_enabled,
            display_name=display_name,
            issuer=issuer,
            authorize_endpoint=authorize_endpoint,
            extra_parameters=extra_parameters,
            token_endpoint=token_endpoint,
            user_info_endpoint=user_info_endpoint,
            introspection_endpoint=introspection_endpoint,
            jwks_uri=jwks_uri,
            client_id=client_id,
            client_secret=client_secret,
            client_auth_method=client_auth_method,
            scopes=scopes,
        )

        return tenant_oidc_configuration
