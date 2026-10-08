from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.server_credentials_api_keys import ServerCredentialsApiKeys
from ...models.server_credentials_oauth_client_credentials import ServerCredentialsOauthClientCredentials
from ...models.server_credentials_oauth_tokens import ServerCredentialsOauthTokens
from ...models.update_mcp_server_credentials_user_response_200 import UpdateMcpServerCredentialsUserResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    *,
    body: ServerCredentialsApiKeys
    | ServerCredentialsOauthClientCredentials
    | ServerCredentialsOauthTokens
    | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/mcp-servers/{server_slug}/credentials/user".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
    }

    if isinstance(body, ServerCredentialsApiKeys):
        _kwargs["json"] = body.to_dict()
    elif isinstance(body, ServerCredentialsOauthTokens):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UpdateMcpServerCredentialsUserResponse200 | None:
    if response.status_code == 200:
        response_200 = UpdateMcpServerCredentialsUserResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UpdateMcpServerCredentialsUserResponse200]:
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
    body: ServerCredentialsApiKeys
    | ServerCredentialsOauthClientCredentials
    | ServerCredentialsOauthTokens
    | Unset = UNSET,
) -> Response[UpdateMcpServerCredentialsUserResponse200]:
    r"""Create or replace the credentials of the authenticated user for an MCP server. The credential type
    must match the authorization method of the server. Servers with transport type \"stdio\" or
    \"hosted\" are restarted to apply the new credentials

    Args:
        server_slug (str):
        body (ServerCredentialsApiKeys | ServerCredentialsOauthClientCredentials |
            ServerCredentialsOauthTokens | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMcpServerCredentialsUserResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServerCredentialsApiKeys
    | ServerCredentialsOauthClientCredentials
    | ServerCredentialsOauthTokens
    | Unset = UNSET,
) -> UpdateMcpServerCredentialsUserResponse200 | None:
    r"""Create or replace the credentials of the authenticated user for an MCP server. The credential type
    must match the authorization method of the server. Servers with transport type \"stdio\" or
    \"hosted\" are restarted to apply the new credentials

    Args:
        server_slug (str):
        body (ServerCredentialsApiKeys | ServerCredentialsOauthClientCredentials |
            ServerCredentialsOauthTokens | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateMcpServerCredentialsUserResponse200
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServerCredentialsApiKeys
    | ServerCredentialsOauthClientCredentials
    | ServerCredentialsOauthTokens
    | Unset = UNSET,
) -> Response[UpdateMcpServerCredentialsUserResponse200]:
    r"""Create or replace the credentials of the authenticated user for an MCP server. The credential type
    must match the authorization method of the server. Servers with transport type \"stdio\" or
    \"hosted\" are restarted to apply the new credentials

    Args:
        server_slug (str):
        body (ServerCredentialsApiKeys | ServerCredentialsOauthClientCredentials |
            ServerCredentialsOauthTokens | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMcpServerCredentialsUserResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServerCredentialsApiKeys
    | ServerCredentialsOauthClientCredentials
    | ServerCredentialsOauthTokens
    | Unset = UNSET,
) -> UpdateMcpServerCredentialsUserResponse200 | None:
    r"""Create or replace the credentials of the authenticated user for an MCP server. The credential type
    must match the authorization method of the server. Servers with transport type \"stdio\" or
    \"hosted\" are restarted to apply the new credentials

    Args:
        server_slug (str):
        body (ServerCredentialsApiKeys | ServerCredentialsOauthClientCredentials |
            ServerCredentialsOauthTokens | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateMcpServerCredentialsUserResponse200
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            body=body,
        )
    ).parsed
