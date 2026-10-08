from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.schema_736 import Schema736

T = TypeVar("T", bound="AssistantLlmConfigurationStatus")


@_attrs_define
class AssistantLlmConfigurationStatus:
    """
    Attributes:
        provider (Schema736): Kind of endpoint that is configured
        model (str): Configured model, deployment or inference profile identifier
        base_url (None | str): Base URL of the endpoint, for an OpenAI-compatible provider
        region (None | str): AWS region, for Bedrock
        resource_name (None | str): Azure OpenAI resource name, for Azure
        api_version (None | str): Azure API version, when one is pinned
        has_api_key (bool): Whether a bearer API key is stored
        has_aws_access_key (bool): Whether an AWS access key pair is stored
    """

    provider: Schema736
    model: str
    base_url: None | str
    region: None | str
    resource_name: None | str
    api_version: None | str
    has_api_key: bool
    has_aws_access_key: bool

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider.value

        model = self.model

        base_url: None | str
        base_url = self.base_url

        region: None | str
        region = self.region

        resource_name: None | str
        resource_name = self.resource_name

        api_version: None | str
        api_version = self.api_version

        has_api_key = self.has_api_key

        has_aws_access_key = self.has_aws_access_key

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "provider": provider,
                "model": model,
                "baseUrl": base_url,
                "region": region,
                "resourceName": resource_name,
                "apiVersion": api_version,
                "hasApiKey": has_api_key,
                "hasAwsAccessKey": has_aws_access_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider = Schema736(d.pop("provider"))

        model = d.pop("model")

        def _parse_base_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        base_url = _parse_base_url(d.pop("baseUrl"))

        def _parse_region(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        region = _parse_region(d.pop("region"))

        def _parse_resource_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        resource_name = _parse_resource_name(d.pop("resourceName"))

        def _parse_api_version(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        api_version = _parse_api_version(d.pop("apiVersion"))

        has_api_key = d.pop("hasApiKey")

        has_aws_access_key = d.pop("hasAwsAccessKey")

        assistant_llm_configuration_status = cls(
            provider=provider,
            model=model,
            base_url=base_url,
            region=region,
            resource_name=resource_name,
            api_version=api_version,
            has_api_key=has_api_key,
            has_aws_access_key=has_aws_access_key,
        )

        return assistant_llm_configuration_status
