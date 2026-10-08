from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="TenantSamlConfiguration")


@_attrs_define
class TenantSamlConfiguration:
    """
    Attributes:
        is_enabled (bool): Whether sign-in through the SAML provider is enabled
        display_name (str): Display name of the identity provider shown on the sign-in page
        idp_metadata_url (str): URL to fetch the IdP metadata document from
        idp_metadata_document (str): Raw IdP metadata XML document
        entry_point (str): URL of the IdP single sign-on endpoint
        cert (str): Certificate used to validate IdP signatures
        identifier_format (str): SAML name identifier format to request
        signature_algorithm (str): Signature algorithm for SAML requests
        email_claim (str): Name of the assertion attribute that holds the email address
        first_name_claim (str): Name of the assertion attribute that holds the first name
        last_name_claim (str): Name of the assertion attribute that holds the last name
    """

    is_enabled: bool
    display_name: str
    idp_metadata_url: str
    idp_metadata_document: str
    entry_point: str
    cert: str
    identifier_format: str
    signature_algorithm: str
    email_claim: str
    first_name_claim: str
    last_name_claim: str

    def to_dict(self) -> dict[str, Any]:
        is_enabled = self.is_enabled

        display_name = self.display_name

        idp_metadata_url = self.idp_metadata_url

        idp_metadata_document = self.idp_metadata_document

        entry_point = self.entry_point

        cert = self.cert

        identifier_format = self.identifier_format

        signature_algorithm = self.signature_algorithm

        email_claim = self.email_claim

        first_name_claim = self.first_name_claim

        last_name_claim = self.last_name_claim

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "isEnabled": is_enabled,
                "displayName": display_name,
                "idpMetadataUrl": idp_metadata_url,
                "idpMetadataDocument": idp_metadata_document,
                "entryPoint": entry_point,
                "cert": cert,
                "identifierFormat": identifier_format,
                "signatureAlgorithm": signature_algorithm,
                "emailClaim": email_claim,
                "firstNameClaim": first_name_claim,
                "lastNameClaim": last_name_claim,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_enabled = d.pop("isEnabled")

        display_name = d.pop("displayName")

        idp_metadata_url = d.pop("idpMetadataUrl")

        idp_metadata_document = d.pop("idpMetadataDocument")

        entry_point = d.pop("entryPoint")

        cert = d.pop("cert")

        identifier_format = d.pop("identifierFormat")

        signature_algorithm = d.pop("signatureAlgorithm")

        email_claim = d.pop("emailClaim")

        first_name_claim = d.pop("firstNameClaim")

        last_name_claim = d.pop("lastNameClaim")

        tenant_saml_configuration = cls(
            is_enabled=is_enabled,
            display_name=display_name,
            idp_metadata_url=idp_metadata_url,
            idp_metadata_document=idp_metadata_document,
            entry_point=entry_point,
            cert=cert,
            identifier_format=identifier_format,
            signature_algorithm=signature_algorithm,
            email_claim=email_claim,
            first_name_claim=first_name_claim,
            last_name_claim=last_name_claim,
        )

        return tenant_saml_configuration
