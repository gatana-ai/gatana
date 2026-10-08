from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_credential_token_response import GetCredentialTokenResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    *,
    credentials_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["credentialsId"] = credentials_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-servers/{server_slug}/credentials/token".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetCredentialTokenResponse | None:
    if response.status_code == 200:
        response_200 = GetCredentialTokenResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetCredentialTokenResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    credentials_id: str | Unset = UNSET,
) -> Response[GetCredentialTokenResponse]:
    """Get the usable token for a credential. For API key credentials, returns the API keys. For OAuth
    credentials, returns the access token, refreshing it first if possible and necessary. When
    credentialsId is omitted, resolves the effective credentials for the current user

    Args:
        server_slug (str):
        credentials_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetCredentialTokenResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        credentials_id=credentials_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    credentials_id: str | Unset = UNSET,
) -> GetCredentialTokenResponse | None:
    """Get the usable token for a credential. For API key credentials, returns the API keys. For OAuth
    credentials, returns the access token, refreshing it first if possible and necessary. When
    credentialsId is omitted, resolves the effective credentials for the current user

    Args:
        server_slug (str):
        credentials_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetCredentialTokenResponse
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        credentials_id=credentials_id,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    credentials_id: str | Unset = UNSET,
) -> Response[GetCredentialTokenResponse]:
    """Get the usable token for a credential. For API key credentials, returns the API keys. For OAuth
    credentials, returns the access token, refreshing it first if possible and necessary. When
    credentialsId is omitted, resolves the effective credentials for the current user

    Args:
        server_slug (str):
        credentials_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetCredentialTokenResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        credentials_id=credentials_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    credentials_id: str | Unset = UNSET,
) -> GetCredentialTokenResponse | None:
    """Get the usable token for a credential. For API key credentials, returns the API keys. For OAuth
    credentials, returns the access token, refreshing it first if possible and necessary. When
    credentialsId is omitted, resolves the effective credentials for the current user

    Args:
        server_slug (str):
        credentials_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetCredentialTokenResponse
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            credentials_id=credentials_id,
        )
    ).parsed
